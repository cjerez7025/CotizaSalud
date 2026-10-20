"""Genera versiones WebP livianas de las fotos de planes (requiere ffmpeg en el PATH).

Uso:  python tools/optimize_images.py

Por cada images/plans/<nombre>.jpg crea:
  images/plans/<nombre>-640.webp   (celulares)
  images/plans/<nombre>-1200.webp  (escritorio)
El .jpg original se conserva (lo usan las vistas previas al compartir el link).
"""
import glob
import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WIDTHS = (640, 1200)
QUALITY = '76'

ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    sys.exit('ffmpeg no esta en el PATH')

before = after = 0
for src in sorted(glob.glob(os.path.join(ROOT, 'images', 'plans', '*.jpg'))):
    base = src[:-4]
    before += os.path.getsize(src)
    for w in WIDTHS:
        out = '%s-%d.webp' % (base, w)
        subprocess.run([ffmpeg, '-y', '-loglevel', 'error', '-i', src,
                        '-vf', "scale='min(%d,iw)':-2" % w,
                        '-c:v', 'libwebp', '-quality', QUALITY, '-compression_level', '6', out], check=True)
        after += os.path.getsize(out)
    print('%-34s %4d KB -> %3d KB + %3d KB' % (os.path.basename(src), os.path.getsize(src) // 1024,
          os.path.getsize('%s-640.webp' % base) // 1024, os.path.getsize('%s-1200.webp' % base) // 1024))
print('jpg total: %d KB | webp (ambos tamanos): %d KB' % (before // 1024, after // 1024))
