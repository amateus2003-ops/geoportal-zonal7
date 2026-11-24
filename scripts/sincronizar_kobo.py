"""Sincroniza la ficha de campo (KoboToolbox) con la base de datos del geoportal (Supabase).

Lo ejecuta GitHub Actions cada hora (.github/workflows/automatizacion-geoportal.yml).

La ficha NO necesita el ID de la alcantarilla: se ubica sola con este orden:
  1. ID de la alcantarilla, si la ficha lo trae;
  2. GPS de la ficha: la alcantarilla del inventario más cercana a 40 m o menos;
  3. abscisa + microempresa: la alcantarilla del tramo de esa micro cuya abscisa estimada
     (scripts/abscisas_alcantarillas.json) está a 120 m o menos.
Si se ubica: las fotos de ANTES/DESPUÉS van a la ventana de la alcantarilla (fotos_alcantarillas)
y la limpieza a reporte_diario. Si no se puede ubicar: las fotos van a la galería del tramo de la
micro (galeria_fotos) y se registra el día de trabajo sin código de alcantarilla.

Las preguntas de la ficha se reconocen por su nombre (se puede cambiar el formulario sin tocar este script):
  microempresa (contiene "micro"), tramo ("tramo" o "via"), abscisa ("absc"), fecha ("fecha"),
  responsable ("respons" o "nombre"), GPS ("gps", "ubic" o "coord"), observaciones ("obs"),
  ID opcional ("codigo" o "id_alc"), fotos: preguntas de imagen cuyo nombre contiene "antes" o "desp";
  cualquier otra foto va a la galería del tramo.

Secretos (GitHub > Settings > Secrets and variables > Actions):
  KOBO_TOKEN, KOBO_ASSET_UID, SUPABASE_SECRET_KEY y opcional KOBO_URL (por defecto https://kf.kobotoolbox.org)
"""
import json, math, os, re, sys, unicodedata, urllib.request, urllib.error

SUPABASE_URL = 'https://zuanqaymtjxmhtizlypj.supabase.co'
BUCKET = 'fotos-campo'
TOL_GPS_M = 40
TOL_ABSCISA_M = 120
MICROEMPRESAS = {  # códigos de la primera versión del formulario
    'm01': "América",
    'm02': "Caminos del Sur",
    'm03': "Conservación Vial Buenavista",
    'm04': "Conservación Vial Puyango",
    'm05': "Divino niño",
    'm06': "Estoraques del Suro",
    'm07': "Larama",
    'm08': "Llankay tantanakuy",
    'm09': "Los Cañaverales",
    'm10': "Niño de Potrerillos",
    'm11': "Paltenses",
    'm12': "Porvenir",
    'm13': "Sabiango",
    'm14': "Tigres del camino",
    'm15': "Virgen del Cisne"
}
KOBO_URL = (os.environ.get('KOBO_URL') or 'https://kf.kobotoolbox.org').rstrip('/')
KOBO_TOKEN = os.environ.get('KOBO_TOKEN', '').strip()
KOBO_ASSET = os.environ.get('KOBO_ASSET_UID', '').strip()
SB_KEY = os.environ.get('SUPABASE_SECRET_KEY', '').strip()
AQUI = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- conexión
def pedir(url, metodo='GET', datos=None, cabeceras=None, crudo=False):
    cab = {'User-Agent': 'geoportal-zonal7-ficha-campo/1.0'}
    cab.update(cabeceras or {})
    req = urllib.request.Request(url, data=datos, method=metodo, headers=cab)
    with urllib.request.urlopen(req, timeout=120) as r:
        cuerpo = r.read()
    return cuerpo if crudo else (json.loads(cuerpo) if cuerpo else None)


def supabase(ruta, metodo='GET', datos=None, extra=None, crudo=False):
    """Clave secreta en 'apikey'; si se rechaza, se reintenta agregando Authorization."""
    base = {'apikey': SB_KEY}
    base.update(extra or {})
    try:
        return pedir(f'{SUPABASE_URL}/{ruta}', metodo, datos, base, crudo)
    except urllib.error.HTTPError as e:
        if e.code not in (401, 403):
            raise
        base['Authorization'] = 'Bearer ' + SB_KEY
        return pedir(f'{SUPABASE_URL}/{ruta}', metodo, datos, base, crudo)


def leer_tabla(consulta):
    filas, desde = [], 0
    while True:
        lote = supabase(f'rest/v1/{consulta}&limit=1000&offset={desde}')
        filas += lote
        if len(lote) < 1000:
            return filas
        desde += 1000


def fichas_kobo():
    url = f'{KOBO_URL}/api/v2/assets/{KOBO_ASSET}/data/?format=json&limit=300'
    while url:
        pagina = pedir(url, cabeceras={'Authorization': f'Token {KOBO_TOKEN}', 'Accept': 'application/json'})
        yield from pagina.get('results', [])
        url = pagina.get('next')


# ---------------------------------------------------------------- lectura de la ficha
def norm(t):
    t = unicodedata.normalize('NFD', str(t or '')).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', t)


def campos(ficha):
    """Preguntas de la ficha como {nombre_corto: valor} (sin metadatos de Kobo ni grupos)."""
    meta = {'start', 'end', 'today', 'deviceid', 'username', 'instanceid', 'version', 'uuid', 'formhub', 'meta'}
    out = {}
    for k, v in ficha.items():
        if k.startswith('_') or v in (None, ''):
            continue
        corto = k.split('/')[-1]
        if corto.lower() in meta or corto.startswith('__'):
            continue
        out[corto] = v
    return out


def buscar(c, *claves, excluir=()):
    for k, v in c.items():
        kl = k.lower()
        if any(x in kl for x in claves) and not any(x in kl for x in excluir):
            return v
    return None


def adjunto(ficha, archivo):
    for a in ficha.get('_attachments', []):
        if archivo in {str(a.get('filename', '')).split('/')[-1], str(a.get('media_file_basename', ''))}:
            return a
    return None


def abscisa_m(valor):
    """'12+345' -> 12345 ; '12.345' o '12,345' (km) -> 12345 ; '12345' -> 12345"""
    s = str(valor or '').strip().lower().replace('km', '').replace(' ', '')
    m = re.match(r'^(\d+)\+(\d+(?:[.,]\d+)?)$', s)
    if m:
        return int(m.group(1)) * 1000 + float(m.group(2).replace(',', '.'))
    try:
        x = float(s.replace(',', '.'))
    except ValueError:
        return None
    return x * 1000 if x < 1000 and ('.' in s or ',' in s) else x


def texto_abscisa(x):
    x = int(round(x))
    return f'{x // 1000}+{x % 1000:03d}'


def distancia_m(lat1, lon1, lat2, lon2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------------------------------------------------------------- ubicación de la alcantarilla
class Inventario:
    def __init__(self):
        d = json.load(open(os.path.join(AQUI, 'abscisas_alcantarillas.json'), encoding='utf-8'))
        self.alc = {int(k): v for k, v in d['alc'].items()}          # id -> [lat, lon, tramo, abscisa_micro]
        self.tramos_micro = d['micro_tramos']                          # micro -> [tramos de la capa]
        self.micros = list(self.tramos_micro)

    def micro(self, valor):
        if not valor:
            return None
        if valor in MICROEMPRESAS:
            return MICROEMPRESAS[valor]
        n = norm(valor)
        for m in self.micros:
            nm = norm(m)
            if n == nm or (len(n) >= 5 and (n in nm or nm in n)):
                return m
        return None

    def ubicar(self, micro, codigo, gps, x):
        if codigo in self.alc:
            return codigo, 'ID de la ficha', 0
        tramos = set(self.tramos_micro.get(micro or '', []))
        cand = [k for k, v in self.alc.items() if v[2] in tramos] if tramos else []
        if gps:
            lat, lon, prec = gps
            if prec is None or prec <= 30:
                pool = cand or list(self.alc)
                k = min(pool, key=lambda k: distancia_m(lat, lon, self.alc[k][0], self.alc[k][1]))
                d = distancia_m(lat, lon, self.alc[k][0], self.alc[k][1])
                if d <= TOL_GPS_M:
                    return k, 'GPS', d
        if x is not None:
            con_abs = [k for k in cand if self.alc[k][3] is not None]
            if con_abs:
                k = min(con_abs, key=lambda k: abs(self.alc[k][3] - x))
                d = abs(self.alc[k][3] - x)
                if d <= TOL_ABSCISA_M:
                    return k, 'abscisa', d
        return None, None, None


# ---------------------------------------------------------------- carga
def main():
    if not (KOBO_TOKEN and KOBO_ASSET and SB_KEY):
        print('Falta configurar KOBO_TOKEN, KOBO_ASSET_UID o SUPABASE_SECRET_KEY en los secretos del repositorio. No se hizo nada.')
        return 0
    inv = Inventario()
    tramo_galeria = {m['nombre']: m.get('tramo') for m in leer_tabla('microempresas?select=nombre,tramo')}
    cargadas = {f['ficha_id'] for f in leer_tabla('reporte_diario?select=ficha_id&ficha_id=not.is.null')}
    json_hdr = {'Content-Type': 'application/json', 'Prefer': 'resolution=ignore-duplicates,return=minimal'}
    ubicadas = sin_ubicar = 0
    for ficha in fichas_kobo():
        ficha_id = 'kobo:' + str(ficha.get('_uuid') or ficha.get('_id'))
        if ficha_id in cargadas:
            continue
        c = campos(ficha)
        micro_txt = buscar(c, 'micro')
        micro = inv.micro(micro_txt)
        tramo_txt = buscar(c, 'tramo', 'via', excluir=('micro',))
        abs_txt = buscar(c, 'absc')
        x = abscisa_m(abs_txt)
        fecha = str(buscar(c, 'fecha') or str(ficha.get('_submission_time', ''))[:10])[:10]
        responsable = buscar(c, 'respons', 'nombre', excluir=('micro', 'tramo'))
        obs = buscar(c, 'obs')
        try:
            codigo = int(str(buscar(c, 'codigo', 'id_alc') or '').strip())
        except ValueError:
            codigo = None
        gps = None
        g = buscar(c, 'gps', 'ubic', 'coord', 'geo')
        if g:
            p = str(g).split()
            try:
                gps = (float(p[0]), float(p[1]), float(p[3]) if len(p) > 3 else None)
            except (ValueError, IndexError):
                gps = None
        objectid, metodo, dist = inv.ubicar(micro, codigo, gps, x)

        # fotos de la ficha: (tipo, pregunta, archivo)
        fotos = []
        for k, v in c.items():
            if isinstance(v, str) and adjunto(ficha, v):
                kl = norm(k)
                tipo = 'antes' if 'antes' in kl else 'despues' if 'desp' in kl else 'otra'
                fotos.append((tipo, k, v))
        carpeta = f'kobo/{objectid}' if objectid else 'kobo/sin_ubicar'
        uuid = ficha_id.split(':', 1)[1]
        orden = {'antes': 0, 'despues': 0}
        if objectid:
            for f in leer_tabla(f'fotos_alcantarillas?select=tipo&objectid=eq.{objectid}'):
                orden[f['tipo']] = orden.get(f['tipo'], 0) + 1
        filas_alc, filas_gal = [], []
        for tipo, pregunta, archivo in fotos:
            a = adjunto(ficha, archivo)
            imagen = pedir(a.get('download_url') or a.get('download_large_url'), cabeceras={'Authorization': f'Token {KOBO_TOKEN}'}, crudo=True)
            ruta = f'{carpeta}/{uuid}_{pregunta}.jpg'
            supabase(f'storage/v1/object/{BUCKET}/{ruta}', 'POST', imagen,
                     {'Content-Type': a.get('mimetype') or 'image/jpeg', 'x-upsert': 'true', 'cache-control': 'max-age=31536000'})
            url = f'{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{ruta}'
            if objectid and tipo in orden:
                orden[tipo] += 1
                filas_alc.append({'objectid': objectid, 'tipo': tipo, 'orden': orden[tipo], 'referencial': False, 'origen': 'KOBO',
                                  'ruta': url, 'archivo_origen': archivo, 'fecha_toma': fecha})
            else:
                filas_gal.append({'microempresa': micro or str(micro_txt or 'SIN MICROEMPRESA'),
                                  'tramo': tramo_galeria.get(micro) or tramo_txt, 'ruta': url, 'fecha_toma': fecha})
        if filas_alc:
            supabase('rest/v1/fotos_alcantarillas?on_conflict=ruta', 'POST', json.dumps(filas_alc).encode(), json_hdr)
        if filas_gal:
            supabase('rest/v1/galeria_fotos?on_conflict=ruta', 'POST', json.dumps(filas_gal).encode(), json_hdr)

        lugar = (f'abscisa {texto_abscisa(x)}' if x is not None else 'sin abscisa') + (f', tramo {tramo_txt}' if tramo_txt else '')
        if objectid:
            nota = f'Alcantarilla ubicada por {metodo}' + (f' (a {dist:.0f} m)' if metodo != 'ID de la ficha' else '')
        else:
            nota = 'No se pudo ubicar la alcantarilla: fotos enviadas a la galería del tramo'
        partes = [str(obs or '').strip(), f'{lugar}. {nota}', f'Ficha de campo KoboToolbox ({responsable or "sin nombre"})']
        reporte = {'ficha_id': ficha_id, 'microempresa': micro or str(micro_txt or 'Sin microempresa'), 'fecha': fecha,
                   'codigo_alcantarilla': str(objectid) if objectid else None, 'estado': 'LIMPIO',
                   'alcantarillas_limpiadas': 1 if objectid else None,
                   'abscisa_inicial': texto_abscisa(x) if x is not None else (str(abs_txt) if abs_txt else None),
                   'coordenadas_utm': f'GPS {gps[0]}, {gps[1]}' if gps else None,
                   'registro_fotografico': f'{len(fotos)} foto(s) de la ficha de campo',
                   'observaciones': ' | '.join(p for p in partes if p)}
        supabase('rest/v1/reporte_diario?on_conflict=ficha_id', 'POST', json.dumps(reporte).encode(), json_hdr)
        cargadas.add(ficha_id)
        if objectid:
            ubicadas += 1
            print(f'✔ {ficha_id}: alcantarilla {objectid} ({nota.lower()}), {reporte["microempresa"]}, {fecha}, {len(fotos)} foto(s)')
        else:
            sin_ubicar += 1
            print(f'• {ficha_id}: {reporte["microempresa"]}, {lugar}: sin ubicar, {len(fotos)} foto(s) a la galería')
    print(f'Fichas nuevas: {ubicadas} ubicadas en una alcantarilla, {sin_ubicar} enviadas a la galería del tramo.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
