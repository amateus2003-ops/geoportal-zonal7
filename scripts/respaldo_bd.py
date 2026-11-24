"""Respaldo automático de la base de datos del geoportal (Supabase).

Lo ejecuta GitHub Actions dos veces por semana (.github/workflows/respaldo-base-de-datos.yml):
  1. Descarga las tablas públicas y las guarda en respaldo_bd/ como JSON.
  2. Con esa consulta el proyecto gratuito de Supabase no se pausa por inactividad.
Si la base no responde, el trabajo falla y GitHub envía un correo de aviso al dueño del repositorio.
Solo usa la clave publicable (la misma del portal): no necesita contraseñas ni claves secretas.
"""
import json, os, sys, urllib.request, urllib.error, datetime

URL = 'https://zuanqaymtjxmhtizlypj.supabase.co'
CLAVE = 'sb_publishable_JcmOdI17wDbayd91ASl27w_IH5fGPox'
TABLAS = {  # tabla: columna para ordenar
    'alcantarillas': 'gid',
    'reporte_diario': 'id',
    'fotos_alcantarillas': 'id',
    'galeria_fotos': 'id',
    'microempresas': 'id',
}
CARPETA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'respaldo_bd')


def leer(tabla, orden):
    filas, desde = [], 0
    while True:
        url = f'{URL}/rest/v1/{tabla}?select=*&order={orden}.asc&limit=1000&offset={desde}'
        req = urllib.request.Request(url, headers={'apikey': CLAVE, 'Accept': 'application/json', 'User-Agent': 'geoportal-zonal7-respaldo/1.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            lote = json.load(r)
        filas += lote
        if len(lote) < 1000:
            return filas
        desde += 1000


def main():
    os.makedirs(CARPETA, exist_ok=True)
    resumen = {}
    for tabla, orden in TABLAS.items():
        try:
            filas = leer(tabla, orden)
        except urllib.error.HTTPError as e:
            detalle = e.read().decode('utf-8', 'replace')[:300]
            sys.exit(f'No se pudo leer {tabla}: HTTP {e.code} {detalle}')
        except urllib.error.URLError as e:
            sys.exit(f'No se pudo leer {tabla}: {e}. Revisa si el proyecto de Supabase está pausado.')
        with open(os.path.join(CARPETA, f'{tabla}.json'), 'w', encoding='utf-8') as f:
            json.dump(filas, f, ensure_ascii=False, indent=0, sort_keys=True)
        resumen[tabla] = len(filas)
        print(f'{tabla}: {len(filas)} filas')
    ahora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))).strftime('%Y-%m-%d %H:%M')
    with open(os.path.join(CARPETA, 'ultima_ejecucion.txt'), 'w', encoding='utf-8') as f:
        f.write(f'Último respaldo: {ahora} (hora de Ecuador)\n')
        for t, n in resumen.items():
            f.write(f'{t}: {n} filas\n')


if __name__ == '__main__':
    main()
