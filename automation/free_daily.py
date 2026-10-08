#!/usr/bin/env python3
"""Pymatec: best-effort free daily discovery, website demos and review-only mail drafts.

Sources: community OpenStreetMap Overpass and the business website itself.
No paid AI, unsolicited sending, fabricated details, or credentials required.
"""
import argparse
import datetime as dt
import hashlib
import html
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import sys
import time
import unicodedata
from urllib.parse import quote, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'auto-demos'
STATE = ROOT / 'automation' / 'seen.json'
REPORTS = ROOT / 'automation' / 'reports'
REPO_URL = 'https://infopymatec-star.github.io/pymatec-demos-andalucia-2026/auto-demos/'
CONTACT = 'info.pymatec@gmail.com'
UA = 'Pymatec-Demo-Research/1.0 (info.pymatec@gmail.com; one limited request daily)'
HEADERS = {'User-Agent': UA, 'Accept-Language': 'es-ES,es;q=0.9'}
CITIES = [
    ('Málaga', 36.7213, -4.4214), ('Granada', 37.1773, -3.5986),
    ('Córdoba', 37.8882, -4.7794), ('Jaén', 37.7796, -3.7849),
    ('Almería', 36.8340, -2.4637), ('Sevilla', 37.3891, -5.9845),
    ('Cádiz', 36.5298, -6.2926), ('Huelva', 37.2614, -6.9447),
    ('Fuengirola', 36.539, -4.624), ('Antequera', 37.019, -4.559),
    ('Ronda', 36.742, -5.165), ('Marbella', 36.510, -4.882),
]
CRAFTS = {
 'plumber': ('Fontanería', '#216F86', 'Fontanería y mantenimiento para tus espacios.'),
 'electrician': ('Instalaciones eléctricas', '#A57220', 'Electricidad e instalaciones para cada necesidad.'),
 'carpenter': ('Carpintería', '#876044', 'Trabajos de carpintería con atención a los detalles.'),
 'painter': ('Pintura', '#42689A', 'Pintura y acabados para transformar espacios.'),
 'roofer': ('Cubiertas y tejados', '#9B5946', 'Especialistas en trabajos de cubiertas y tejados.'),
 'gardener': ('Jardinería', '#38785B', 'Jardinería para espacios exteriores.'),
 'tiler': ('Alicatados y solados', '#98664F', 'Alicatados y revestimientos con buenos acabados.'),
 'glaziery': ('Cristalería', '#3D788F', 'Cristalería y soluciones para tus espacios.'),
 'floorer': ('Pavimentos', '#826248', 'Soluciones profesionales para pavimentos.'),
 'hvac': ('Climatización', '#266D7F', 'Climatización e instalaciones para viviendas y negocios.'),
 'handyman': ('Mantenimiento', '#43756A', 'Servicios de mantenimiento para tus instalaciones.'),
}
BAD_EMAIL = ('noreply@', 'no-reply@', 'wordpress@', 'sentry@', 'example.com', 'wix.com', 'godaddy.com')
BAD_HOSTS = ('facebook.com','instagram.com','linkedin.com','twitter.com','x.com','youtube.com','tiktok.com','amazon.es','ebay.es','google.com','wa.me','goo.gl')
ECOM_INDICATORS = ('añadir al carrito', 'add to cart', 'finalizar compra', 'checkout', 'mi cesta', 'woocommerce-cart', 'shopify-payment-button')

def slugify(text):
    normal = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode('ascii')
    return re.sub('-+', '-', re.sub('[^a-z0-9]+','-', normal.lower())).strip('-')[:55] or 'empresa'

def public_site(url):
    if not url: return None
    url = str(url).strip().split(';')[0]
    if '://' not in url: url = 'https://' + url
    u = urlparse(url)
    if u.scheme not in ('http','https') or not u.hostname: return None
    host = u.hostname.lower().strip('.')
    if host in ('localhost','metadata.google.internal') or host.endswith(('.local','.internal','.test')): return None
    if any(host == p or host.endswith('.'+p) for p in BAD_HOSTS): return None
    try:
        ip = ipaddress.ip_address(host)
        if not ip.is_global: return None
    except ValueError:
        pass
    return url

def domain(url):
    return (urlparse(url).hostname or '').lower().removeprefix('www.')

def overpass(city):
    city_name, lat, lon = city
    # A single small query each day; the public instance may legitimately deny a busy query.
    q = f'''[out:json][timeout:24];(
    nwr(around:11000,{lat},{lon})["craft"]["name"]["website"];
    );out tags center 100;'''
    resp = requests.post('https://overpass-api.de/api/interpreter', data={'data': q}, headers=HEADERS, timeout=39)
    resp.raise_for_status()
    return (resp.json().get('elements') or []), city_name

def choose(elements, seen):
    options = []
    dups = set()
    for obj in elements:
        t = obj.get('tags') or {}
        craft = t.get('craft')
        if craft not in CRAFTS: continue
        name = (t.get('name') or '').strip()
        site = public_site(t.get('website') or t.get('contact:website') or '')
        if not name or len(name)>110 or not site: continue
        host = domain(site)
        if host in seen or host in dups: continue
        dups.add(host)
        options.append({'name':name,'website':site,'domain':host,'craft':craft,'osm_id':str(obj.get('id'))})
    return options[:30]

def safe_request(url):
    if not public_site(url): raise ValueError('URL no pública')
    r = requests.get(url, headers=HEADERS, timeout=13, allow_redirects=True)
    if len(r.content) > 1000000 or not public_site(r.url): raise ValueError('Respuesta inválida')
    r.raise_for_status()
    if 'text/html' not in r.headers.get('Content-Type','text/html'): raise ValueError('Sin página HTML')
    return r

def valid_email(email):
    email = email.strip().strip('<>.;:,').lower()
    return bool(re.fullmatch(r'[\w.\-+]+@[a-z0-9.\-]+\.[a-z]{2,}',email)) and not any(x in email for x in BAD_EMAIL)

def extract_email(soup):
    emails = []
    for a in soup.select('a[href^="mailto:"]'):
        candidate = a['href'][7:].split('?')[0].strip()
        if valid_email(candidate): emails.append(candidate)
    if not emails:
        for candidate in re.findall(r'[\w.\-+]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}',soup.get_text(' ',strip=True)):
            if valid_email(candidate): emails.append(candidate.lower())
    return emails[0] if emails else None

def extract_logo(soup, base_url):
    for img in soup.find_all('img')[:90]:
        path = img.get('data-src') or img.get('src') or ''
        if not path or path.startswith(('data:','javascript:')): continue
        evidence = ' '.join([path,img.get('alt') or '', ' '.join(img.get('class') or [])]).lower()
        if not any(k in evidence for k in ('logo','logotipo','marca','brand')): continue
        img_url = public_site(urljoin(base_url,path))
        if img_url and (domain(img_url)==domain(base_url) or domain(img_url).endswith('.'+domain(base_url))):
            return img_url
    return None

def extract_business(option):
    r = safe_request(option['website'])
    soup = BeautifulSoup(r.text, 'html.parser')
    for el in soup(['script','style','noscript','template']): el.decompose()
    visible = soup.get_text(' ',strip=True).lower()
    if any(k in visible for k in ECOM_INDICATORS): return None
    email = extract_email(soup)
    # One contact-page request at most if the main page has no business email.
    if not email:
        links = [a for a in soup.select('a[href]') if any(w in (a.get_text(' ',strip=True)+' '+a['href']).lower() for w in ('contacto','contact','contactar'))]
        for a in links[:2]:
            u = public_site(urljoin(r.url,a['href']))
            if not u or domain(u)!=domain(r.url): continue
            try:
                rr = safe_request(u)
                email = extract_email(BeautifulSoup(rr.text,'html.parser'))
                if email: break
            except (requests.RequestException,ValueError): pass
    if not email: return None
    logo = extract_logo(soup,r.url)
    theme = soup.select_one('meta[name="theme-color"]')
    palette = CRAFTS[option['craft']][1]
    theme_value = theme.get('content','') if theme else ''
    if re.fullmatch('#[0-9a-fA-F]{6}',theme_value): palette = theme_value
    tel = soup.select_one('a[href^="tel:"]')
    phone = tel.get('href','')[4:].strip() if tel else ''
    if len(phone)>35 or not re.fullmatch(r'[+0-9 ()\-]*',phone): phone=''
    return {**option, 'email':email, 'logo':logo, 'color':palette, 'phone':phone, 'verified_url':r.url}

def clean(s): return html.escape(str(s),quote=True)

def make_demo(info, city):
    name, craft = info['name'], info['craft']
    sector, _, desc = CRAFTS[craft]
    color = info['color']
    title = f'{sector} en {city}'
    slug = slugify(name)+'-'+hashlib.sha256(info['domain'].encode()).hexdigest()[:5]
    logo = (f'<img class="logo" src="{clean(info["logo"])}" alt="Logo de {clean(name)}" loading="eager" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'block\'">' if info['logo'] else '')
    lettermark = f'<span class="wordmark" {"style=display:none" if info["logo"] else ""}>{clean(name)}</span>'
    photo = {
      'carpenter':'photo-1601058268499-e52658b8bb88', 'electrician':'photo-1621905252507-b35492cc74b4',
      'plumber':'photo-1585704032915-c3400ca199e7','gardener':'photo-1416879595882-3373a0480b5b',
      'painter':'photo-1562259949-e8e7689d7828', 'roofer':'photo-1504307651254-35680f356dfd',
    }.get(craft,'photo-1504307651254-35680f356dfd')
    photo_url='https://images.unsplash.com/'+photo+'?auto=format&fit=crop&w=1800&q=80'
    display_phone = clean(info['phone']) if info['phone'] else ''
    phone_html = f'<a href="tel:{clean(info["phone"])}">{display_phone}</a>' if display_phone else '<span>Consultar por correo</span>'
    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><meta name="description" content="Demo conceptual no oficial Pymatec · {clean(name)}"><title>{clean(name)} · Propuesta Pymatec</title><style>
:root{{--brand:{color};--ink:#21313d;--muted:#65717a;--cream:#f6f5f1}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;font:16px/1.65 system-ui,-apple-system,sans-serif;color:var(--ink)}}.wrap{{max-width:1190px;margin:auto;padding:0 5%}}.note{{font-size:10px;padding:8px 12px;text-align:center;background:#f3f5f6;letter-spacing:.08em;font-weight:700}}header{{background:#fff;position:sticky;top:0;z-index:10;border-bottom:1px solid #e9e9e9}}nav{{min-height:86px;display:flex;justify-content:space-between;align-items:center;gap:24px}}.logo{{max-height:58px;max-width:200px;object-fit:contain}}.wordmark{{font-size:21px;font-weight:850;letter-spacing:-.04em}}a{{text-decoration:none;color:inherit}}.button{{background:var(--brand);color:#fff;display:inline-block;padding:15px 23px;border-radius:40px;font-weight:750}}.hero{{background:linear-gradient(90deg,#18202bdd,#18202b77),url('{photo_url}') center/cover;min-height:640px;color:#fff;display:flex;align-items:center}}.eyebrow{{text-transform:uppercase;font-size:11px;letter-spacing:.19em;font-weight:800}}h1{{font-size:clamp(43px,7vw,92px);line-height:1.06;letter-spacing:-.065em;max-width:900px;margin:22px 0}}h2{{font-size:clamp(30px,4vw,54px);line-height:1.15;letter-spacing:-.06em}}.hero p{{max-width:640px;font-size:19px}}.section{{padding:95px 0}}.soft{{background:var(--cream)}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:65px;align-items:start}}.service{{padding:29px;border:1px solid #e3e5e5;background:#fff;border-radius:19px;min-height:185px}}.service b{{display:block;font-size:21px;letter-spacing:-.025em}}.service p{{color:var(--muted)}}.contact{{background:#f7f7f4;border:1px solid #e5e5e1;padding:27px;border-radius:24px}}.entry{{display:grid;grid-template-columns:100px 1fr;gap:16px;padding:19px 0;border-bottom:1px solid #e1e1da}}.entry:last-child{{border:0}}.entry small{{text-transform:uppercase;letter-spacing:.12em;color:var(--brand);font-weight:800}}.entry a,.entry span{{overflow-wrap:anywhere}}.banner{{background:linear-gradient(90deg,#1f303fbf,#1f303f7d),url('{photo_url}') center/cover;color:white;padding:75px 0}}footer{{padding:28px 0;font-size:12px;color:#606b71}}footer a{{text-decoration:underline}}@media(max-width:750px){{nav{{min-height:72px}}.wordmark{{font-size:18px}}.hero{{min-height:565px}}.grid{{grid-template-columns:1fr;gap:15px}}.section{{padding:65px 0}}.entry{{grid-template-columns:1fr;gap:4px}}.button{{font-size:13px}}}}
</style></head><body><div class="note">PROPUESTA DE DISEÑO NO OFICIAL · NO ENCARGADA NI VALIDADA POR LA EMPRESA · PYMATEC</div><header><nav class="wrap"><div>{logo}{lettermark}</div><a class="button" href="#contacto">Solicitar presupuesto ↗</a></nav></header><main><section class="hero"><div class="wrap"><div class="eyebrow">{clean(sector)} · {clean(city)}</div><h1>{clean(title)}.<br>Una presencia más actual.</h1><p>{clean(desc)} Una propuesta de presentación más clara, pensada para móviles y para facilitar el contacto.</p><a class="button" href="#contacto">Pide información ↗</a></div></section><section class="section soft" id="servicios"><div class="wrap"><div class="eyebrow">01 · Especialidad</div><h2>Lo importante, a primera vista.</h2><div class="grid"><div class="service"><b>{clean(sector)}</b><p>Presentación de la actividad según el perfil público de la empresa.</p></div><div class="service"><b>Presupuestos</b><p>Contacto directo para consultar condiciones, alcance y disponibilidad.</p></div></div></div></section><section class="section"><div class="wrap grid"><div><div class="eyebrow">02 · Una web para conectar</div><h2>Un espacio que representa mejor tu trabajo.</h2><p>Este diseño es una maqueta conceptual para mostrar una posible mejora de la presencia digital de {clean(name)}. Las fotografías son ilustrativas.</p></div><div><p style="font-size:20px;margin-top:70px;color:var(--muted)">Una web más clara, con información esencial y acceso sencillo al contacto desde cualquier dispositivo.</p></div></div></section><section class="banner"><div class="wrap"><div class="eyebrow">03 · El siguiente paso</div><h2>¿Hablamos de tu proyecto?</h2><a class="button" href="#contacto">Solicitar presupuesto ↗</a></div></section><section class="section" id="contacto"><div class="wrap grid"><div><div class="eyebrow">04 · Contacto</div><h2>Hablemos.</h2><p>Datos encontrados en la web pública de la empresa; deben ser confirmados antes de una publicación oficial.</p></div><div class="contact"><div class="entry"><small>Teléfono</small>{phone_html}</div><div class="entry"><small>Email</small><a href="mailto:{clean(info['email'])}">{clean(info['email'])}</a></div><div class="entry"><small>Web oficial</small><a href="{clean(info['verified_url'])}" target="_blank" rel="noopener noreferrer">Visitar sitio original ↗</a></div></div></div></section></main><footer><div class="wrap">Propuesta de rediseño no oficial creada por Pymatec. No representa a {clean(name)} ni implica su aprobación. Datos de descubrimiento: OpenStreetMap © colaboradores (ODbL). <a href="{clean(info['verified_url'])}">Fuente oficial de contacto</a>.</div></footer></body></html>'''
    return slug, doc

def gmail_compose(email,subject,body):
    # Opens a pre-filled compose view. This is NOT a saved Gmail draft and never sends.
    return 'https://mail.google.com/mail/?view=cm&fs=1&to='+quote(email,safe='@')+'&su='+quote(subject,safe='')+'&body='+quote(body,safe='')

def create_note(entry, date):
    """Prepare the same email copy for every business; only the demo URL changes.

    The Gmail compose link is not a saved draft and does not send email.
    The reviewer must verify prior lawful authorisation for commercial sending.
    """
    email, demo = entry['email'], entry['demo_url']
    subj = 'Propuesta de rediseño web · Pymatec'
    template = (ROOT / 'automation' / 'email_tipo.md').read_text(encoding='utf-8')
    if template.count('{{ENLACE_WEB}}') != 1:
        raise ValueError('La plantilla debe incluir una sola variable {{ENLACE_WEB}}')
    body = template.replace('{{ENLACE_WEB}}', demo)
    note = f'Para: {email}\nAsunto: {subj}\n\n{body}'
    plain = body.replace(f'**[Enlace web]({demo})**', demo)
    plain = plain.replace('[https://pymatec.es](https://pymatec.es)', 'https://pymatec.es')
    plain = plain.replace('**', '')
    return note, gmail_compose(email, subj, plain)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--demo-test', action='store_true', help='offline local fake data test')
    opts=parser.parse_args()
    day=dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=2))).date().isoformat()
    DEST.mkdir(exist_ok=True)
    STATE.parent.mkdir(exist_ok=True)
    REPORTS.mkdir(exist_ok=True)
    seen=set(json.loads(STATE.read_text()).get('domains',[])) if STATE.exists() else set()
    # Skip pilot domains to avoid rediscovering users' initial five.
    seen.update(['laureanoramos.es','logarze.es','instalacionesmesa.com','carpinterosjaen.com','oryxobrasyservicios.com'])
    if opts.demo_test:
        city='Málaga'
        lead={'name':'TALLER DE PRUEBA - NO PUBLICAR','website':'https://example.net','domain':'example.net','craft':'carpenter','email':'ejemplo@example.net','logo':None,'color':'#876044','phone':'+34950000000','verified_url':'https://example.net'}
        slug,html_content=make_demo(lead,city)
        assert 'PROPUESTA DE DISEÑO NO OFICIAL' in html_content
        assert 'mailto:ejemplo@example.net' in html_content
        mail, compose = create_note({'email':'ejemplo@example.net', 'demo_url':'https://example.net/demo/'}, '2026-10-08')
        assert mail.count('https://example.net/demo/') == 1
        assert 'Presupuesto cerrado: 490 € + IVA.' in mail
        assert 'Podéis verlo aquí:' in mail
        assert 'restauración y contacto' in mail
        assert 'view=cm' in compose and 'https%3A%2F%2Fexample.net%2Fdemo%2F' in compose
        print('TEST OK: generated HTML, safe noindex, contact. No file saved.')
        return
    idx=dt.date.fromisoformat(day).toordinal()%len(CITIES)
    city=CITIES[idx]
    records=[]; problems=[]
    try:
        options,city_name=overpass(city)
        options=choose(options,seen)
    except Exception as ex:
        problems.append(f'No se pudo consultar la fuente pública para {city[0]}: {type(ex).__name__}.')
        options=[];city_name=city[0]
    for item in options:
        if len(records)>=5: break
        try:
            lead=extract_business(item)
        except Exception:
            lead=None
        if lead is None: continue
        slug,content=make_demo(lead,city_name)
        folder=DEST/slug
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'index.html').write_text(content,encoding='utf-8')
        demo=REPO_URL+slug+'/'
        entry={**lead,'slug':slug,'demo_url':demo,'city':city_name,'date':day}
        mail,compose=create_note(entry,day)
        (folder/'propuesta-email.txt').write_text(mail,encoding='utf-8')
        entry['compose_url']=compose
        records.append(entry)
        seen.add(lead['domain'])
        print('PREPARADA',lead['name'],demo)
        time.sleep(1.2)
    STATE.write_text(json.dumps({'domains':sorted(seen),'updated':day},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # The public report is review-only, not permission to send commercial messages.
    lines=[f'# Pymatec · propuestas del {day}', '',f'Área explorada: **{city_name} y alrededores**.', '',
           '**Solo para revisión. Ningún mensaje ha sido enviado.**', '',
           'No puede garantizarse encontrar cinco contactos verificados cada día. Las fuentes gratuitas pueden fallar o limitar búsquedas.', '']
    for i,e in enumerate(records,1):
        lines.extend([f'## {i}. {e["name"]}',f'- Demo: {e["demo_url"]}',
                      f'- Web original: {e["verified_url"]}',f'- Email público verificado: {e["email"]}',
                      f'- [Abrir propuesta de correo (sin enviar)]({e["compose_url"]})',
                      f'- Texto del email: `auto-demos/{e["slug"]}/propuesta-email.txt`',''])
    if not records: lines+=['No se han encontrado empresas que cumplan todos los filtros hoy.','']
    if problems: lines+=['**Limitaciones:**']+['- '+x for x in problems]+['']
    lines+=['Los correos públicos **no autorizan** por sí solos comunicaciones comerciales no solicitadas (LSSI, art. 21). Revisar base legal antes de cualquier envío.','',
            'Fuente de candidatos: OpenStreetMap © colaboradores. Cada email se verifica en la web pública de la empresa.','']
    report='\n'.join(lines)
    (REPORTS/(day+'.md')).write_text(report,encoding='utf-8')
    (ROOT/'automation'/'issue-body.md').write_text(report,encoding='utf-8')
    pages=[]
    for path in sorted(DEST.iterdir()):
        if path.is_dir() and (path/'index.html').exists():
            pages.append(f'<li><a href="{clean(path.name)}/">{clean(path.name)}</a></li>')
    (DEST/'index.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Propuestas Pymatec · Demo</title><style>body{font:17px/1.8 system-ui;margin:50px auto;padding:0 25px;max-width:850px;color:#23313c}a{color:#237b88}small{color:#777}</style><small>Propuestas no oficiales · Pymatec</small><h1>Demostraciones de diseño web</h1><p>Propuestas conceptuales basadas en datos públicos. No son webs oficiales ni implican colaboración con las empresas.</p><ul>'+''.join(pages[:350])+'</ul><p>OpenStreetMap © colaboradores.</p></html>',encoding='utf-8')
    print('TOTAL',len(records),'AREA',city_name,'REPORTE',REPORTS/(day+'.md'))

if __name__=='__main__': main()
