import re, json, html, sys

sys.path.insert(0, __import__('os').path.dirname(__file__))
from plans_meta import SLUGS, SLIDE_SLUGS


def clean(t):
    return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()


def extract(src):
    """Devuelve {slug: datos} leyendo las fichas y los slides de index_13.html.

    Las fichas siguen el orden de SLUGS; los slides, el de SLIDE_SLUGS. Un plan sin
    slide queda con eyebrow/blurb/img vacios (se completan desde plan_details.NEW_PLANS).
    """
    cards = re.findall(r'<div class="plan-card[^"]*">(.*?)</a>\s*</div>', src, re.S)
    slides = re.findall(r'<div class="slide slide-\d+" id="slide\d+">(.*?)</div>\s*</div>', src, re.S)
    assert len(cards) == len(SLUGS), (len(cards), len(SLUGS))
    assert len(slides) == len(SLIDE_SLUGS), (len(slides), len(SLIDE_SLUGS))
    by_slide = {}
    for slug, s in zip(SLIDE_SLUGS, slides):
        by_slide[slug] = dict(
            img=re.search(r'<img class="slide-bg" src="([^"]+)"', s).group(1),
            eyebrow=clean(re.search(r'class="slide-eyebrow">(.*?)</span>', s, re.S).group(1)),
            title=clean(re.search(r'<h3>(.*?)</h3>', s, re.S).group(1)),
            blurb=clean(re.search(r'<p>(.*?)</p>', s, re.S).group(1)))
    plans = {}
    for slug, c in zip(SLUGS, cards):
        name = clean(re.search(r'<h3>(.*?)</h3>', c, re.S).group(1))
        tag = clean(re.search(r'<p class="plan-tag">(.*?)</p>', c, re.S).group(1))
        feats = [clean(x) for x in re.findall(r'<li><span class="check">.*?</span>(.*?)</li>', c, re.S)]
        pl = re.search(r'<span class="from">(.*?)</span><br><span class="amt">(.*?)</span>', c, re.S)
        price_label = clean(pl.group(1))
        price_val = clean(pl.group(2).replace('<sup>', ' ').replace('</sup>', ''))
        d = dict(name=name, tag=tag, feats=feats, price_label=price_label, price=price_val,
                 img='', eyebrow='', title='', blurb='')
        d.update(by_slide.get(slug, {}))
        plans[slug] = d
    return plans


if __name__ == '__main__':
    print(json.dumps(extract(open(sys.argv[1], encoding='utf-8').read()), ensure_ascii=False, indent=1))
