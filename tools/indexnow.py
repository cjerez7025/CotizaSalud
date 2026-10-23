"""Avisa a los buscadores que usan IndexNow (Bing y otros) de las URLs del sitio.

Uso (despues de publicar):  python tools/indexnow.py

Lee las URLs de sitemap.xml y las envia a https://api.indexnow.org/IndexNow.
La llave es publica por diseno: el buscador la verifica leyendo
https://cotizasaludchile.cl/<llave>.txt, que debe estar publicado.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

HOST = 'cotizasaludchile.cl'
KEY = '6c4f1b0e9a7d4c2e8b35f1a9d07e24c6'
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

urls = re.findall(r'<loc>(.*?)</loc>', open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read())
payload = {'host': HOST, 'key': KEY, 'keyLocation': 'https://%s/%s.txt' % (HOST, KEY), 'urlList': urls}
req = urllib.request.Request('https://api.indexnow.org/IndexNow', data=json.dumps(payload).encode('utf-8'),
                             headers={'Content-Type': 'application/json; charset=utf-8'}, method='POST')
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print('IndexNow respondio', r.status, 'para', len(urls), 'URLs')
except urllib.error.HTTPError as e:
    print('IndexNow respondio', e.code, e.reason, '(200 y 202 = aceptado)')
    sys.exit(1)
