"""Genera las paginas internas del sitio a partir de index_13.html.

Uso (desde la raiz del repo):  python tools/build_pages.py

Produce:
  assets/site.css, assets/pages.css
  planes/index.html y planes/<slug>/index.html   (una pagina por plan)
  guias/isapre-vs-fonasa-seguro-complementario/index.html
  sitemap.xml

Los datos de cada plan (nombre, tope, beneficios) se leen de las fichas de
index_13.html; asi, si cambias un valor alli y vuelves a correr el script, las
paginas internas quedan al dia. El texto editorial propio de cada plan vive en
PLAN_COPY, mas abajo.
"""
import html as H
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from extract_plans import extract
from plans_meta import SLUGS

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE = 'https://cotizasaludchile.cl'
TODAY = '2026-10-19'
GUIDE_SLUG = 'isapre-vs-fonasa-seguro-complementario'


def esc(t):
    return H.escape(t, quote=False)


def attr(t):
    return H.escape(t, quote=True)


# --------------------------------------------------------------------------
# Contenido editorial por plan. Solo usa datos que ya estan en el sitio.
# --------------------------------------------------------------------------
PLAN_COPY = {
    'cuidado-total-70': dict(
        display='Bupa Cuidado Total 70',
        who='Pueden contratarlo afiliados a Isapre o a Fonasa.',
        fit='Es el plan más elegido. Te sirve si quieres atenderte en clínicas de libre elección con una bonificación alta (70%), tener consultas y videoconsultas ilimitadas y dejar maternidad, salud mental y urgencias dentro de la cobertura. Si el presupuesto es lo que más pesa, compáralo con Cuidado Total 60.',
        related=['cuidado-total-60', 'seguro-catastrofico', 'complementa']),
    'cuidado-total-60': dict(
        display='Bupa Cuidado Total 60',
        who='Pueden contratarlo afiliados a Isapre o a Fonasa.',
        fit='Mantiene la lógica de libre elección y la cobertura de maternidad, salud mental y urgencias del plan 70, con 60% de bonificación y un tope anual menor (UF 250 frente a UF 400). Es la opción si quieres bajar el costo sin cambiar de tipo de plan.',
        related=['cuidado-total-70', 'seguro-catastrofico', 'proteccion-ambulatorio-70']),
    'seguro-catastrofico': dict(
        display='Seguro Bupa Catastrófico',
        who='Pueden contratarlo afiliados a Isapre o a Fonasa.',
        lead='Cobertura ante enfermedades de alto costo: hasta 100% de cobertura, deducible $0 en 5 patologías graves y hasta UF 30.000 por evento.',
        fit='Está pensado para el riesgo de alto costo, no para el gasto del día a día: cubre enfermedades graves con hasta UF 30.000 por evento y deducible $0 en 5 patologías. Funciona como una capa de protección sobre tu Isapre o Fonasa. Si además quieres cubrir consultas y exámenes habituales, mira Cuidado Total.',
        related=['cuidado-total-70', 'proteccion-80-70', 'multisalud']),
    'proteccion-80-70': dict(
        display='Bupa + Protección 80/70',
        who='Es exclusivo para afiliados a Fonasa.',
        fit='Es para afiliados a Fonasa que quieren cobertura hospitalaria alta (80%) y ambulatoria (70%) sin deducible, con atención en Clínica Bupa Santiago y en la red IntegraMédica. Incluye extensión catastrófica y seguro de vida por muerte accidental. Si prefieres 70% también en hospitalización, revisa + Protección 70/70.',
        related=['proteccion-70-70', 'multisalud', 'proteccion-ambulatorio-70']),
    'proteccion-70-70': dict(
        display='Bupa + Protección 70/70',
        who='Es exclusivo para afiliados a Fonasa.',
        fit='Tiene la misma estructura que + Protección 80/70, pero con 70% de cobertura tanto hospitalaria como ambulatoria. Es para afiliados a Fonasa que buscan una cobertura pareja, sin deducible, con extensión catastrófica y seguro de vida incluido.',
        related=['proteccion-80-70', 'proteccion-ambulatorio-70', 'multisalud']),
    'proteccion-ambulatorio-70': dict(
        display='Bupa + Protección Ambulatorio 70',
        who='Es exclusivo para afiliados a Fonasa y cubre solo atención ambulatoria.',
        fit='Es la opción liviana: solo ambulatorio. Te sirve si quieres reducir el copago de consultas, exámenes e imágenes y no necesitas cobertura hospitalaria. Si te preocupa una hospitalización, + Protección 70/70 suma esa cobertura.',
        related=['proteccion-70-70', 'proteccion-80-70', 'multisalud']),
    'multisalud': dict(
        display='Bupa MultiSalud',
        who='Es exclusivo para afiliados a Fonasa de los tramos B, C o D.',
        fit='Es para afiliados a Fonasa (tramos B, C o D) que quieren elegir entre 3 redes de prestadores y llegar hasta 90% de cobertura en la red preferente, con extensión catastrófica de hasta UF 7.500 adicionales. Tiene el tope anual más alto de las opciones para Fonasa del sitio (UF 1.500).',
        related=['proteccion-80-70', 'proteccion-70-70', 'seguro-catastrofico']),
    'complementa': dict(
        display='Bupa Complementa',
        who='Está pensado para quienes ya tienen Isapre.',
        fit='Si ya tienes Isapre y lo que te pesa es el copago, este plan lo cubre al mismo porcentaje que tu plan de Isapre, sin deducible y sin declaración de salud. Incluye hospitalización, oncología y maternidad.',
        related=['cuidado-total-70', 'seguro-catastrofico', 'integramedica-100']),
    'integramedica-100': dict(
        display='Plan IntegraMédica 100% de Bupa',
        who='Pueden contratarlo afiliados a Isapre y a Fonasa, sin declaración de salud (DPS).',
        fit='Está pensado para quien tiene enfermedades preexistentes o no quiere pasar por una declaración de salud. Cubre el 100% del copago en consultas, exámenes e imágenes dentro de la red IntegraMédica, sin deducible.',
        related=['adulto-mayor-integramedica-70', 'complementa', 'cuidado-total-60']),
    'pymes-70-smart': dict(
        display='Bupa Pymes 70 Smart',
        who='Es para empresas desde 5 colaboradores.',
        fit='Es para empresas desde 5 colaboradores que quieren ofrecer cobertura de salud a su equipo: sin deducible, con tarifa única por tramo sin importar el tamaño de la empresa, telemedicina 100% sin tope y 10% adicional en prestaciones IntegraMédica. Se cotiza por titular.',
        related=['cuidado-total-70', 'seguro-catastrofico', 'integramedica-100']),
    'adulto-mayor-integramedica-70': dict(
        display='Plan Adulto Mayor IntegraMédica 70',
        who='Pueden contratarlo personas desde los 60 años, afiliadas a Isapre o a Fonasa.',
        fit='Está pensado para personas desde los 60 años: cubre enfermedades ya diagnosticadas (sin preexistencias), con 70% en consultas, exámenes e imagenología y rescate de riesgo vital 24/7 en todo Chile.',
        related=['integramedica-100', 'complementa', 'cuidado-total-60']),
}

HUB_GROUPS = [
    ('Isapre o Fonasa', 'Planes que pueden contratar afiliados a cualquiera de los dos sistemas.',
     ['cuidado-total-70', 'cuidado-total-60', 'seguro-catastrofico', 'integramedica-100']),
    ('Exclusivos para Fonasa', 'Planes pensados para afiliados a Fonasa.',
     ['proteccion-80-70', 'proteccion-70-70', 'proteccion-ambulatorio-70', 'multisalud']),
    ('Si ya tienes Isapre', 'Un seguro que cubre el copago de tu plan actual.', ['complementa']),
    ('Adultos mayores', 'Cobertura desde los 60 años, sin preexistencias.', ['adulto-mayor-integramedica-70']),
    ('Empresas y pymes', 'Salud para tu equipo, desde 5 colaboradores.', ['pymes-70-smart']),
]


# --------------------------------------------------------------------------
# Piezas compartidas, leidas desde index_13.html
# --------------------------------------------------------------------------
def load_shared(src):
    css = re.search(r'<style>(.*?)</style>', src, re.S).group(1)
    sprite = re.search(r'<svg style="position:absolute;width:0;height:0;overflow:hidden;" aria-hidden="true">.*?</svg>', src, re.S).group(0)
    header = re.search(r'<header>.*?</header>', src, re.S).group(0)
    footer = re.search(r'<footer>.*?</footer>', src, re.S).group(0)
    wsp = re.search(r'<a href="#" class="wsp-float js-wsp-link".*?</a>', src, re.S).group(0)
    icon = re.search(r'<link rel="icon"[^>]*>', src).group(0)
    fonts = '\n'.join(re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*fonts[^>]*>|<link href="https://fonts[^>]*>', src))
    webapp = re.search(r"var COTIZA_WEBAPP_URL = '([^']+)'", src).group(1)

    def fix_hash(m):
        name = m.group(1)
        return 'href="/planes/"' if name == 'planes' else 'href="/#%s"' % name
    header = re.sub(r'href="#(\w+)"', fix_hash, header)
    footer = re.sub(r'href="#(\w+)"', lambda m: 'href="/#%s"' % m.group(1), footer)
    header = re.sub(r'<div class="logo">(.*?)</div>', r'<a class="logo" href="/" aria-label="CotizaSalud Chile, inicio">\1</a>', header, count=1, flags=re.S)
    footer = re.sub(r'<div class="logo">(.*?)</div>', r'<a class="logo" href="/" aria-label="CotizaSalud Chile, inicio">\1</a>', footer, count=1, flags=re.S)
    return dict(css=css, sprite=sprite, header=header, footer=footer, wsp=wsp, icon=icon, fonts=fonts, webapp=webapp)


PAGES_CSS = '''/* Estilos de las paginas internas (planes, guias). Complementa site.css. */
.crumbs{font-size:13px;color:var(--slate);margin:0 0 22px;display:flex;flex-wrap:wrap;gap:6px;align-items:center;}
.crumbs a{color:var(--teal-deep);}
.crumbs a:hover{text-decoration:underline;}
.crumbs .sep{opacity:.5;}
.page-hero{padding:40px 0 56px;}
.ph-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center;}
.page-hero h1{font-size:clamp(28px,3.6vw,44px);margin:6px 0 16px;color:var(--ink);}
.page-hero .lead{font-size:17px;line-height:1.6;color:var(--slate);margin:0 0 22px;max-width:560px;}
.ph-price{display:inline-flex;flex-direction:column;gap:2px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 20px;margin:0 0 24px;box-shadow:var(--shadow-sm);}
.ph-price .from{font-size:12px;color:var(--slate);}
.ph-price .amt{font-family:'IBM Plex Mono',monospace;font-size:28px;font-weight:600;color:var(--ink);}
.ph-price .amt small{font-size:14px;color:var(--slate);font-weight:400;}
.ph-ctas{display:flex;gap:12px;flex-wrap:wrap;}
.ph-img{border-radius:20px;overflow:hidden;box-shadow:var(--shadow-md);aspect-ratio:4/3;background:var(--teal-pale);}
.ph-img img{width:100%;height:100%;object-fit:cover;}
.page-body{padding:0 0 72px;}
.content-grid{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,.65fr);gap:44px;align-items:start;}
.prose h2{font-size:clamp(21px,2.4vw,27px);margin:44px 0 14px;}
.prose h2:first-child{margin-top:0;}
.prose h3{font-size:18px;margin:28px 0 10px;}
.prose p{color:var(--slate);font-size:16px;line-height:1.75;margin:0 0 16px;}
.prose p a,.prose li a{color:var(--teal-deep);text-decoration:underline;}
.prose ul.bullets{margin:0 0 18px;padding-left:20px;list-style:disc;}
.prose ul.bullets li{color:var(--slate);font-size:16px;line-height:1.7;margin-bottom:8px;}
.big-feats{margin:0 0 8px;}
.big-feats li{display:flex;gap:12px;align-items:flex-start;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:10px;font-size:16px;color:var(--ink-soft);line-height:1.45;}
.facts{position:sticky;top:96px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:24px;box-shadow:var(--shadow-sm);}
.facts h2{font-size:17px;margin:0 0 4px;}
.facts dl{margin:0;}
.facts dt{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--slate);font-weight:600;margin-top:16px;}
.facts dd{margin:3px 0 0;font-size:15px;color:var(--ink);font-weight:500;line-height:1.45;}
.facts .btn{width:100%;margin-top:22px;}
.related-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:8px;}
.related-card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px;transition:border-color .18s ease, box-shadow .18s ease;}
.related-card:hover{border-color:var(--teal);box-shadow:var(--shadow-md);}
.related-card h3{font-size:16px;margin:0 0 6px;color:var(--ink);}
.related-card p{font-size:13px;color:var(--slate);margin:0 0 14px;flex:1;line-height:1.5;}
.related-card span{font-size:13.5px;font-weight:600;color:var(--teal-deep);}
.disclaimer{font-size:12.5px;color:var(--slate);line-height:1.6;border-top:1px solid var(--line);padding-top:18px;margin-top:36px;}
.cta-band{background:var(--ink);color:#fff;border-radius:24px;padding:48px 40px;text-align:center;margin-top:56px;}
.cta-band h2{color:#fff;font-size:clamp(22px,2.8vw,30px);margin:0 0 12px;}
.cta-band p{color:#B9C6CF;margin:0 auto 24px;max-width:520px;line-height:1.6;}
.cta-band .ph-ctas{justify-content:center;}
.hub-group{margin-bottom:44px;}
.hub-group .related-grid{grid-template-columns:repeat(auto-fill,minmax(250px,1fr));}
.hub-group h2{font-size:22px;margin-bottom:6px;}
.hub-group > p{color:var(--slate);margin:0 0 18px;}
.table-scroll{overflow-x:auto;margin:8px 0 24px;}
.cmp-table{width:100%;border-collapse:collapse;font-size:14.5px;background:var(--card);border:1px solid var(--line);}
.cmp-table th,.cmp-table td{padding:14px 16px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);line-height:1.5;color:var(--slate);}
.cmp-table th{background:var(--teal-pale);color:var(--ink);font-family:'Montserrat',sans-serif;font-size:13px;}
.cmp-table td:first-child{font-weight:600;color:var(--ink);}
.article-meta{font-size:13px;color:var(--slate);margin:0 0 24px;}
.article-wrap{max-width:780px;margin:0 auto;}
@media (max-width:980px){
  .ph-grid{grid-template-columns:1fr;gap:28px;}
  .content-grid{grid-template-columns:1fr;gap:32px;}
  .facts{position:static;}
  .related-grid{grid-template-columns:1fr;}
}
@media (max-width:760px){
  .page-hero{padding:28px 0 40px;}
  .cta-band{padding:36px 22px;}
}
'''


def phone_script(webapp):
    return '''<script>
(function(){
  var URL_ = '%s';
  try{
    fetch(URL_, { method: 'GET' })
      .then(function(r){ return r.json(); })
      .then(function(data){
        if(!data) return;
        var ej = data.ejecutiva || {};
        var tel = ej.telefono || data.celular;
        if(!tel) return;
        var d = tel.toString().replace(/[^0-9]/g, '');
        if(!d) return;
        var wsp = 'https://wa.me/' + d + '?text=' + encodeURIComponent('Hola, quiero cotizar un seguro de salud Bupa');
        document.querySelectorAll('.js-wsp-link').forEach(function(a){ a.setAttribute('href', wsp); });
        document.querySelectorAll('.js-phone-number').forEach(function(el){ el.textContent = tel; });
        document.querySelectorAll('.js-phone-tel').forEach(function(a){ a.setAttribute('href', 'tel:+' + d); });
      })
      .catch(function(e){ console.error('config celular error', e); });
  }catch(e){ console.error('config celular error', e); }
})();
</script>''' % shared['webapp']


def ld(obj):
    return '<script type="application/ld+json">\n%s\n</script>' % json.dumps(obj, ensure_ascii=False, indent=2)


def page(title, desc, path, body, jsonld, og_image, og_type='website'):
    url = SITE + path
    return '''<!DOCTYPE html>
<html lang="es-CL">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="es_CL">
<meta property="og:site_name" content="CotizaSalud Chile">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_image}">
{icon}
{fonts}
<link rel="stylesheet" href="/assets/site.css">
<link rel="stylesheet" href="/assets/pages.css">
{jsonld}
<script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script>
<script defer src="/_vercel/insights/script.js"></script>
</head>
<body>
{sprite}
{header}
<main>
{body}
</main>
{footer}
{wsp}
{script}
</body>
</html>
'''.format(title=attr(title), desc=attr(desc), url=url, og_type=og_type, og_image=og_image, body=body,
           icon=shared['icon'], fonts=shared['fonts'], jsonld='\n'.join(jsonld),
           sprite=shared['sprite'], header=shared['header'], footer=shared['footer'],
           wsp=shared['wsp'], script=phone_script(shared['webapp']))


def crumbs(items):
    out = []
    for i, (label, href) in enumerate(items):
        if i:
            out.append('<span class="sep" aria-hidden="true">›</span>')
        out.append('<a href="%s">%s</a>' % (href, esc(label)) if href else '<span aria-current="page">%s</span>' % esc(label))
    return '<nav class="crumbs" aria-label="Migas de pan">%s</nav>' % ' '.join(out)


def breadcrumb_ld(items):
    return ld({
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': name, 'item': SITE + href}
            for i, (name, href) in enumerate(items)],
    })


def price_text(price):
    return price.replace(' /', '/')


def ctas(label='Cotizar este plan'):
    return ('<div class="ph-ctas"><a href="/#contacto" class="btn btn-primary">%s</a>'
            '<a href="#" class="btn btn-wsp js-wsp-link" target="_blank" rel="noopener">'
            '<svg class="icon-wsp" aria-hidden="true"><use href="#icon-wsp"></use></svg> Hablar por WhatsApp</a></div>' % label)


def cta_band(name):
    return ('<div class="cta-band"><h2>Cotiza %s sin costo</h2>'
            '<p>Cuéntame tu caso y te envío tu propuesta con valores reales en menos de 24 horas, sin compromiso.</p>%s</div>' % (esc(name), ctas('Cotizar ahora')))


DISCLAIMER = ('<p class="disclaimer">Información referencial. Valores en UF, sujetos a tu edad y composición familiar. '
              'Coberturas, topes y condiciones dependen de las condiciones generales y particulares de la póliza vigente de Bupa Seguros.</p>')


# --------------------------------------------------------------------------
# Paginas
# --------------------------------------------------------------------------
def build_plan(plan, slug, by_slug):
    c = PLAN_COPY[slug]
    d = c['display']
    lead = c.get('lead', plan['blurb'])
    path = '/planes/%s/' % slug
    price = price_text(plan['price'])
    is_from = plan['price_label'].lower() == 'desde'
    tag_parts = [t.strip() for t in plan['tag'].split('·')]

    faqs = [
        ('¿Qué cubre %s?' % d, '%s. Además: %s.' % (lead.rstrip('.'), '; '.join(f[0].lower() + f[1:] for f in plan['feats']))),
        ('¿Quién puede contratar %s?' % d, c['who']),
    ]
    if is_from:
        faqs.append(('¿Cuánto cuesta %s?' % d,
                     'Tiene un valor referencial desde %s. El precio final depende de tu edad y de tu composición familiar; al cotizar recibes los valores reales para tu caso.' % price))
    else:
        faqs.append(('¿Cuál es el tope de cobertura de %s?' % d,
                     'El tope anual es %s. Es el máximo que el plan cubre al año, no el valor de la prima: el costo mensual depende de tu edad y de tu composición familiar, y lo recibes con valores reales al cotizar.' % price))

    jsonld = [
        breadcrumb_ld([('Inicio', '/'), ('Planes', '/planes/'), (d, path)]),
        ld({'@context': 'https://schema.org', '@type': 'Service', 'name': d,
            'serviceType': 'Seguro complementario de salud', 'description': lead,
            'url': SITE + path, 'areaServed': 'CL',
            'provider': {'@type': 'Organization', 'name': 'Bupa Seguros'},
            'broker': {'@type': 'InsuranceAgency', 'name': 'CotizaSalud Chile', 'url': SITE + '/'}}),
        ld({'@context': 'https://schema.org', '@type': 'FAQPage',
            'mainEntity': [{'@type': 'Question', 'name': q,
                            'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faqs]}),
    ]

    feats = ''.join('<li><span class="check">✓</span><span>%s</span></li>' % esc(f) for f in plan['feats'])
    faq_html = ''.join('<details class="faq-item"><summary>%s</summary><p>%s</p></details>' % (esc(q), esc(a)) for q, a in faqs)
    related = ''.join(
        '<a class="related-card" href="/planes/%s/"><h3>%s</h3><p>%s</p><span>Ver detalle →</span></a>'
        % (r, esc(PLAN_COPY[r]['display']), esc(by_slug[r]['tag'])) for r in c['related'])

    body = '''<section class="page-hero">
  <div class="wrap ph-grid">
    <div>
      {crumbs}
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      <p class="lead">{blurb}</p>
      <div class="ph-price"><span class="from">{label}</span><span class="amt">{price}</span></div>
      {ctas}
    </div>
    <div class="ph-img"><img src="/{img}" alt="{alt}" width="1050" height="700" loading="eager"></div>
  </div>
</section>
<section class="page-body">
  <div class="wrap">
    <div class="content-grid">
      <div class="prose">
        <h2>Qué incluye {name}</h2>
        <ul class="big-feats">{feats}</ul>
        <h2>¿Es el plan para ti?</h2>
        <p>{fit}</p>
        <h2>Preguntas frecuentes sobre {name}</h2>
        <div class="faq-list">{faqs}</div>
        {disclaimer}
      </div>
      <aside class="facts">
        <h2>Datos clave</h2>
        <dl>
          <dt>Se contrata con</dt><dd>{tag}</dd>
          <dt>{label}</dt><dd>{price}</dd>
          <dt>Quién puede contratarlo</dt><dd>{who}</dd>
          <dt>Cotización</dt><dd>Gratis, con respuesta en menos de 24 horas</dd>
        </dl>
        <a href="/#contacto" class="btn btn-primary">Cotizar este plan</a>
      </aside>
    </div>
    <div class="prose" style="margin-top:56px;">
      <h2>Otros planes que podrían interesarte</h2>
      <div class="related-grid">{related}</div>
      <p style="margin-top:20px;"><a href="/planes/">Ver todos los planes Bupa →</a></p>
    </div>
    {band}
  </div>
</section>'''.format(
        crumbs=crumbs([('Inicio', '/'), ('Planes', '/planes/'), (d, None)]),
        eyebrow=esc(plan['eyebrow']), h1=esc('%s: qué cubre y cómo cotizarlo' % d), blurb=esc(lead),
        label=esc(plan['price_label']), price=esc(price), ctas=ctas(), img=plan['img'], alt=attr('%s, seguro de salud Bupa' % d),
        name=esc(d), feats=feats, fit=esc(c['fit']), faqs=faq_html, disclaimer=DISCLAIMER,
        tag=esc(' · '.join(tag_parts)), who=esc(c['who']), related=related, band=cta_band(d))

    title = '%s: cobertura y cotización | CotizaSalud Chile' % d
    if len(title) > 65:
        title = '%s: cobertura y cotización' % d
    desc = '%s Cotiza gratis %s con tu ejecutiva Bupa Seguros.' % (lead.rstrip('.') + '.', d)
    if len(desc) > 165:
        desc = desc[:162].rsplit(' ', 1)[0] + '…'
    return path, page(title, desc, path, body, jsonld, '%s/%s' % (SITE, plan['img']))


def build_hub(plans, by_slug):
    path = '/planes/'
    groups = []
    for title, intro, slugs in HUB_GROUPS:
        cards = ''.join(
            '<a class="related-card" href="/planes/%s/"><h3>%s</h3><p>%s<br>%s %s</p><span>Ver detalle →</span></a>'
            % (s, esc(PLAN_COPY[s]['display']), esc(by_slug[s]['tag']),
               esc(by_slug[s]['price_label']), esc(price_text(by_slug[s]['price']))) for s in slugs)
        groups.append('<div class="hub-group"><h2>%s</h2><p>%s</p><div class="related-grid">%s</div></div>' % (esc(title), esc(intro), cards))
    jsonld = [
        breadcrumb_ld([('Inicio', '/'), ('Planes', path)]),
        ld({'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Planes de seguro de salud Bupa en Chile',
            'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': PLAN_COPY[s]['display'], 'url': '%s/planes/%s/' % (SITE, s)}
                                for i, s in enumerate(SLUGS)]}),
    ]
    body = '''<section class="page-hero" style="padding-bottom:32px;">
  <div class="wrap">
    {crumbs}
    <span class="eyebrow">Planes disponibles</span>
    <h1>Planes de seguro de salud Bupa en Chile</h1>
    <p class="lead">{n} planes de Bupa Seguros para afiliados a Isapre y Fonasa, adultos mayores y empresas. Elige uno para ver qué cubre, o cuéntame tu caso y te recomiendo el que mejor se ajusta.</p>
    {ctas}
  </div>
</section>
<section class="page-body">
  <div class="wrap">
    {groups}
    {disclaimer}
    {band}
  </div>
</section>'''.format(crumbs=crumbs([('Inicio', '/'), ('Planes', None)]), n=len(SLUGS), ctas=ctas('Cotizar gratis'),
                     groups=''.join(groups), disclaimer=DISCLAIMER, band=cta_band('tu seguro de salud'))
    title = 'Planes de seguro de salud Bupa en Chile | CotizaSalud Chile'
    desc = 'Compara los 11 planes de salud Bupa: Cuidado Total, + Protección, MultiSalud, Catastrófico, Complementa, pymes y adulto mayor. Cotiza gratis.'
    return path, page(title, desc, path, body, jsonld, SITE + '/images/plans/cuidado-total-70.jpg')


ARTICLE = '''<section class="page-hero" style="padding-bottom:32px;">
  <div class="wrap article-wrap">
    {crumbs}
    <span class="eyebrow">Guía</span>
    <h1>Isapre vs Fonasa: qué conviene y cómo te ayuda un seguro complementario</h1>
    <p class="article-meta">Publicado el 19 de octubre de 2026 · Lectura de 5 minutos</p>
  </div>
</section>
<section class="page-body">
  <div class="wrap article-wrap prose">
    <p>Elegir entre Isapre y Fonasa es una de las decisiones de salud más importantes que toma una familia en Chile, y no tiene una respuesta única: depende de tu ingreso, tu edad, tu estado de salud y dónde quieres atenderte. Lo que sí es común a ambos sistemas es que ninguno cubre el 100% de los gastos médicos. La diferencia entre lo que cuesta una atención y lo que tu sistema paga es el <strong>copago</strong>, y ahí es donde entra un seguro complementario.</p>

    <h2>Fonasa en pocas palabras</h2>
    <p>Fonasa es el sistema público de salud. Cotizas el 7% de tu renta imponible (hasta el tope legal) y accedes a atención en la red pública. También puedes atenderte con prestadores privados mediante la modalidad de libre elección, donde Fonasa bonifica una parte del valor según tu tramo (A, B, C o D). El monto que pagas depende de tu ingreso, no de tu edad ni de tus enfermedades.</p>

    <h2>Isapre en pocas palabras</h2>
    <p>Las Isapres son aseguradoras privadas. Contratas un plan que define la red de prestadores, el porcentaje de cobertura y un precio expresado en UF. La cotización legal es el 7% de tu renta, pero el precio del plan puede ser mayor y la diferencia la pagas tú. El valor del plan puede variar según tu edad, sexo y número de cargas, y al ingresar pueden pedirte una declaración de salud. Revisa siempre las condiciones de tu contrato.</p>

    <h2>Comparación rápida</h2>
    <div class="table-scroll"><table class="cmp-table">
      <thead><tr><th></th><th>Fonasa</th><th>Isapre</th></tr></thead>
      <tbody>
        <tr><td>Quién lo administra</td><td>Sistema público</td><td>Aseguradoras privadas</td></tr>
        <tr><td>Cómo se paga</td><td>7% de tu renta imponible</td><td>7% de tu renta como mínimo, más lo que cueste tu plan</td></tr>
        <tr><td>Qué influye en el costo</td><td>Tu ingreso</td><td>Tu plan, edad, sexo y cargas</td></tr>
        <tr><td>Dónde te atiendes</td><td>Red pública o prestadores privados con bonificación</td><td>La red de prestadores de tu plan</td></tr>
        <tr><td>Copago</td><td>Depende de tu tramo y del prestador</td><td>Depende del plan que contrataste</td></tr>
      </tbody>
    </table></div>

    <h2>Lo que ninguno de los dos cubre del todo: el copago</h2>
    <p>Una hospitalización en clínica, un examen de imágenes o una consulta con un especialista de libre elección casi siempre dejan un saldo por pagar, aunque estés bien afiliado. Un seguro complementario de salud se suma a tu Isapre o Fonasa y reembolsa o bonifica parte de ese saldo. No reemplaza a tu sistema de salud: lo complementa.</p>

    <h2>Qué seguro complementario va con cada sistema</h2>
    <ul class="bullets">
      <li><strong>Si estás en Fonasa:</strong> existen planes exclusivos, como <a href="/planes/proteccion-80-70/">+ Protección 80/70</a>, <a href="/planes/proteccion-70-70/">+ Protección 70/70</a>, <a href="/planes/proteccion-ambulatorio-70/">+ Protección Ambulatorio 70</a> y <a href="/planes/multisalud/">MultiSalud</a> (tramos B, C o D).</li>
      <li><strong>Si ya tienes Isapre:</strong> <a href="/planes/complementa/">Bupa Complementa</a> cubre el copago al mismo porcentaje que tu plan actual, sin deducible y sin declaración de salud.</li>
      <li><strong>En cualquiera de los dos:</strong> <a href="/planes/cuidado-total-70/">Cuidado Total 70</a>, <a href="/planes/cuidado-total-60/">Cuidado Total 60</a>, el <a href="/planes/seguro-catastrofico/">Seguro Catastrófico</a> y el <a href="/planes/integramedica-100/">Plan IntegraMédica 100%</a>, que no pide declaración de salud.</li>
      <li><strong>Desde los 60 años:</strong> <a href="/planes/adulto-mayor-integramedica-70/">Adulto Mayor IntegraMédica 70</a>.</li>
      <li><strong>Para empresas:</strong> <a href="/planes/pymes-70-smart/">Pymes 70 Smart</a>, desde 5 colaboradores.</li>
    </ul>

    <h2>Preguntas para decidir</h2>
    <ul class="bullets">
      <li>¿En qué clínicas u hospitales quiero atenderme normalmente?</li>
      <li>¿Qué copago puedo pagar sin que me complique el presupuesto si hay una hospitalización?</li>
      <li>¿Tengo enfermedades preexistentes que condicionen qué plan puedo contratar?</li>
      <li>¿Busco cobertura para el día a día, para eventos graves o para ambos?</li>
      <li>¿Es solo para mí o para mi familia?</li>
    </ul>
    <p>Si ya estás en Isapre o Fonasa y estás conforme con tu sistema, normalmente no necesitas cambiarte para mejorar tu cobertura: un seguro complementario es la forma más directa de reducir lo que pagas de tu bolsillo.</p>

    <p class="disclaimer">Esta guía es informativa y simplifica un sistema que cambia con la normativa. Para confirmar tus condiciones, consulta tu contrato, Fonasa o la Superintendencia de Salud. Las coberturas de los planes Bupa dependen de las condiciones de cada póliza.</p>

    {band}
  </div>
</section>'''


def build_article():
    path = '/guias/%s/' % GUIDE_SLUG
    title = 'Isapre vs Fonasa: qué conviene y seguro complementario'
    desc = 'Diferencias entre Isapre y Fonasa en Chile y cómo un seguro complementario de salud reduce tus copagos. Guía clara para decidir.'
    jsonld = [
        breadcrumb_ld([('Inicio', '/'), ('Isapre vs Fonasa', path)]),
        ld({'@context': 'https://schema.org', '@type': 'Article',
            'headline': 'Isapre vs Fonasa: qué conviene y cómo te ayuda un seguro complementario',
            'description': desc, 'datePublished': TODAY, 'dateModified': TODAY, 'inLanguage': 'es-CL',
            'mainEntityOfPage': SITE + path,
            'image': SITE + '/images/plans/cuidado-total-70.jpg',
            'author': {'@type': 'Organization', 'name': 'CotizaSalud Chile', 'url': SITE + '/'},
            'publisher': {'@type': 'Organization', 'name': 'CotizaSalud Chile', 'url': SITE + '/'}}),
    ]
    body = ARTICLE.replace('{crumbs}', crumbs([('Inicio', '/'), ('Guías', None), ('Isapre vs Fonasa', None)])) \
                  .replace('{band}', cta_band('tu seguro complementario'))
    return path, page(title, desc, path, body, jsonld, SITE + '/images/plans/cuidado-total-70.jpg', og_type='article')


def build_sitemap(paths):
    rows = [('/', '1.0', 'weekly')]
    for p in paths:
        pr = '0.9' if p == '/planes/' else '0.8' if p.startswith('/planes/') else '0.7'
        rows.append((p, pr, 'monthly'))
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, pr, cf in rows:
        out.append('  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>' % (SITE, p, TODAY, cf, pr))
    out.append('</urlset>')
    return '\n'.join(out) + '\n'


def write(rel, content):
    full = os.path.join(ROOT, rel.lstrip('/'))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)


if __name__ == '__main__':
    src = open(os.path.join(ROOT, 'index_13.html'), encoding='utf-8').read()
    shared = load_shared(src)
    plans = extract(src)
    assert len(plans) == len(SLUGS) == len(PLAN_COPY), (len(plans), len(SLUGS), len(PLAN_COPY))
    by_slug = dict(zip(SLUGS, plans))

    write('assets/site.css', shared['css'].strip() + '\n')
    write('assets/pages.css', PAGES_CSS)

    paths = []
    p, html_ = build_hub(plans, by_slug)
    write(p + 'index.html', html_); paths.append(p)
    for slug, plan in by_slug.items():
        p, html_ = build_plan(plan, slug, by_slug)
        write(p + 'index.html', html_); paths.append(p)
    p, html_ = build_article()
    write(p + 'index.html', html_); paths.append(p)

    write('sitemap.xml', build_sitemap(paths))
    print('ok:', len(paths), 'paginas')
