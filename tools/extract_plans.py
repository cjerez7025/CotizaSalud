import re, json, html, sys

def clean(t):
    return html.unescape(re.sub(r'<[^>]+>', '', t)).strip()

def extract(src):
    cards = re.findall(r'<div class="plan-card[^"]*">(.*?)</a>\s*</div>', src, re.S)
    slides = re.findall(r'<div class="slide slide-\d+" id="slide\d+">(.*?)</div>\s*</div>', src, re.S)
    plans = []
    for c, s in zip(cards, slides):
        name = clean(re.search(r'<h3>(.*?)</h3>', c, re.S).group(1))
        tag = clean(re.search(r'<p class="plan-tag">(.*?)</p>', c, re.S).group(1))
        feats = [clean(x) for x in re.findall(r'<li><span class="check">.*?</span>(.*?)</li>', c, re.S)]
        pl = re.search(r'<span class="from">(.*?)</span><br><span class="amt">(.*?)</span>', c, re.S)
        price_label = clean(pl.group(1))
        price_val = clean(pl.group(2).replace('<sup>', ' ').replace('</sup>', ''))
        img = re.search(r'<img class="slide-bg" src="([^"]+)"', s).group(1)
        eyebrow = clean(re.search(r'class="slide-eyebrow">(.*?)</span>', s, re.S).group(1))
        title = clean(re.search(r'<h3>(.*?)</h3>', s, re.S).group(1))
        blurb = clean(re.search(r'<p>(.*?)</p>', s, re.S).group(1))
        plans.append(dict(name=name, tag=tag, feats=feats, price_label=price_label,
                          price=price_val, img=img, eyebrow=eyebrow, title=title, blurb=blurb))
    return plans

if __name__ == '__main__':
    p = extract(open(sys.argv[1], encoding='utf-8').read())
    print(len(p))
    print(json.dumps(p, ensure_ascii=False, indent=1))
