"""Sincroniza la ficha de campo (KoboToolbox) con la base de datos del geoportal (Supabase).

Lo ejecuta GitHub Actions cada hora (.github/workflows/automatizacion-geoportal.yml).
Por cada ficha nueva:
  1. descarga sus fotos de Kobo y las sube a Supabase Storage (carpeta fotos-campo/kobo/...),
  2. registra las fotos en fotos_alcantarillas (antes / después),
  3. registra la limpieza en reporte_diario (con ficha_id para no repetirla).
Una ficha con un ID de alcantarilla que no existe no se carga y se informa en el registro del trabajo.

Secretos que necesita (GitHub > Settings > Secrets and variables > Actions):
  KOBO_TOKEN          clave API de KoboToolbox (Account settings > Security)
  KOBO_ASSET_UID      identificador del formulario (aparece en la dirección: /forms/<UID>/summary)
  SUPABASE_SECRET_KEY clave secreta de Supabase (Project Settings > API Keys > Secret keys)
Opcional: KOBO_URL (por defecto https://kf.kobotoolbox.org)
"""
import json, os, sys, urllib.request, urllib.error, urllib.parse

SUPABASE_URL = 'https://zuanqaymtjxmhtizlypj.supabase.co'
BUCKET = 'fotos-campo'
MICROEMPRESAS = {  # opciones del formulario (hoja choices, lista "micro")
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
CAMPOS_FOTO = [('antes', 'foto_antes_1'), ('antes', 'foto_antes_2'), ('despues', 'foto_despues_1'), ('despues', 'foto_despues_2')]

KOBO_URL = (os.environ.get('KOBO_URL') or 'https://kf.kobotoolbox.org').rstrip('/')
KOBO_TOKEN = os.environ.get('KOBO_TOKEN', '').strip()
KOBO_ASSET = os.environ.get('KOBO_ASSET_UID', '').strip()
SB_KEY = os.environ.get('SUPABASE_SECRET_KEY', '').strip()


def pedir(url, metodo='GET', datos=None, cabeceras=None, crudo=False):
    req = urllib.request.Request(url, data=datos, method=metodo, headers=cabeceras or {})
    with urllib.request.urlopen(req, timeout=120) as r:
        cuerpo = r.read()
    return cuerpo if crudo else (json.loads(cuerpo) if cuerpo else None)


def supabase(ruta, metodo='GET', datos=None, extra=None, crudo=False):
    """Llama a Supabase con la clave secreta. Prueba primero solo con 'apikey' y, si se rechaza, agrega Authorization."""
    url = f'{SUPABASE_URL}/{ruta}'
    base = {'apikey': SB_KEY}
    base.update(extra or {})
    try:
        return pedir(url, metodo, datos, base, crudo)
    except urllib.error.HTTPError as e:
        if e.code not in (401, 403):
            raise
        base['Authorization'] = 'Bearer ' + SB_KEY
        return pedir(url, metodo, datos, base, crudo)


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


def adjunto(ficha, archivo):
    for a in ficha.get('_attachments', []):
        nombres = {str(a.get('filename', '')).split('/')[-1], str(a.get('media_file_basename', ''))}
        if archivo in nombres:
            return a
    return None


def main():
    if not (KOBO_TOKEN and KOBO_ASSET and SB_KEY):
        print('Falta configurar KOBO_TOKEN, KOBO_ASSET_UID o SUPABASE_SECRET_KEY en los secretos del repositorio. No se hizo nada.')
        return 0
    cargadas = {f['ficha_id'] for f in leer_tabla('reporte_diario?select=ficha_id&ficha_id=not.is.null')}
    validos = {int(f['objectid']) for f in leer_tabla('alcantarillas?select=objectid')}
    nuevas = rechazadas = 0
    for ficha in fichas_kobo():
        ficha_id = 'kobo:' + str(ficha.get('_uuid') or ficha.get('_id'))
        if ficha_id in cargadas:
            continue
        try:
            codigo = int(str(ficha.get('codigo', '')).strip())
        except ValueError:
            codigo = None
        if codigo not in validos:
            rechazadas += 1
            print(f'⚠ Ficha {ficha_id} ({ficha.get("fecha")}, {ficha.get("responsable")}): el ID de alcantarilla "{ficha.get("codigo")}" no existe. No se cargó.')
            continue
        micro = MICROEMPRESAS.get(ficha.get('microempresa'), ficha.get('microempresa') or 'Sin microempresa')
        fecha = str(ficha.get('fecha') or str(ficha.get('_submission_time', ''))[:10])
        existentes = leer_tabla(f'fotos_alcantarillas?select=tipo&objectid=eq.{codigo}')
        orden = {'antes': sum(f['tipo'] == 'antes' for f in existentes), 'despues': sum(f['tipo'] == 'despues' for f in existentes)}
        filas_fotos = []
        for tipo, campo in CAMPOS_FOTO:
            archivo = ficha.get(campo)
            if not archivo:
                continue
            a = adjunto(ficha, archivo)
            if not a:
                print(f'  · {ficha_id}: no se encontró el adjunto {archivo}')
                continue
            imagen = pedir(a.get('download_url') or a.get('download_large_url'), cabeceras={'Authorization': f'Token {KOBO_TOKEN}'}, crudo=True)
            ruta = f'kobo/{codigo}/{ficha_id.split(":")[1]}_{campo}.jpg'
            supabase(f'storage/v1/object/{BUCKET}/{ruta}', 'POST', imagen,
                     {'Content-Type': a.get('mimetype') or 'image/jpeg', 'x-upsert': 'true', 'cache-control': 'max-age=31536000'})
            orden[tipo] += 1
            filas_fotos.append({'objectid': codigo, 'tipo': tipo, 'orden': orden[tipo], 'referencial': False, 'origen': 'KOBO',
                                'ruta': f'{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{ruta}',
                                'archivo_origen': archivo, 'fecha_toma': fecha})
        json_hdr = {'Content-Type': 'application/json', 'Prefer': 'resolution=ignore-duplicates,return=minimal'}
        if filas_fotos:
            supabase('rest/v1/fotos_alcantarillas?on_conflict=ruta', 'POST', json.dumps(filas_fotos).encode(), json_hdr)
        gps = str(ficha.get('ubicacion') or '').split()
        partes = [str(ficha.get('observaciones') or '').strip(),
                  f'Nivel de colmatación: {ficha["colmatacion"]}' if ficha.get('colmatacion') else '',
                  f'Ficha de campo KoboToolbox ({ficha.get("responsable") or "sin nombre"})']
        reporte = {'ficha_id': ficha_id, 'microempresa': micro, 'fecha': fecha, 'codigo_alcantarilla': str(codigo),
                   'estado': 'LIMPIO', 'alcantarillas_limpiadas': 1,
                   'coordenadas_utm': f'GPS {gps[0]}, {gps[1]}' if len(gps) >= 2 else None,
                   'registro_fotografico': f'{len(filas_fotos)} foto(s) de la ficha de campo',
                   'observaciones': ' | '.join(p for p in partes if p)}
        supabase('rest/v1/reporte_diario?on_conflict=ficha_id', 'POST', json.dumps(reporte).encode(), json_hdr)
        cargadas.add(ficha_id)
        nuevas += 1
        print(f'✔ {ficha_id}: alcantarilla {codigo}, {micro}, {fecha}, {len(filas_fotos)} foto(s)')
    print(f'Fichas nuevas cargadas: {nuevas}. Rechazadas por ID inexistente: {rechazadas}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
