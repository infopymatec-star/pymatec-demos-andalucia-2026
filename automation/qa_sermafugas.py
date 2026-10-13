"""Valida con Chromium la maqueta Sermafugas en móvil y escritorio."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'auto-demos'/'grupo-sermafugas'
PAGES=['index.html','servicios.html','camara-inspeccion.html','geofono.html','gas-trazador.html',
       'termografia.html','logger-sonido.html','balsas-riego.html','cubiertas-tejados.html',
       'sobre-nosotros.html','contacto.html','privacidad.html']
errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
    try:
        for name in PAGES:
            file=DIR/name
            if not file.exists():errors.append('Falta '+name);continue
            for width,height in [(1280,800),(390,844)]:
                page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
                try:
                    page.goto(file.as_uri(),wait_until='domcontentloaded',timeout=25000)
                    for x in page.locator('img').all():
                        try:
                            x.evaluate("e => e.loading = 'eager'")
                            x.scroll_into_view_if_needed(timeout=1400)
                        except Exception:pass
                    page.wait_for_timeout(2200)
                    data=page.evaluate("""() => ({
                      viewport: innerWidth,scroll: document.documentElement.scrollWidth,
                      images: [...document.images].map(i=>({src:i.src,loaded:i.complete&&i.naturalWidth>0,visible:i.getBoundingClientRect().width>40&&i.getBoundingClientRect().height>35})),
                      nav: [...document.querySelectorAll('nav a[href]')].map(a=>a.getAttribute('href')),
                      links: [...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')),
                      logos: [...document.querySelectorAll('.site-logo img,.footer-logo img')].map(i=>i.complete&&i.naturalWidth>0),
                      menuVisible: getComputedStyle(document.querySelector('.nav-toggle')).display,
                    })""")
                    if data['scroll']>width+8:errors.append(name+' '+str(width)+': overflow '+str(data['scroll']))
                    if len(data['logos'])!=2 or not all(data['logos']):errors.append(name+' '+str(width)+': logotipo de cabecera o pie no carga')
                    for i in data['images']:
                        if not i['loaded'] or not i['visible']:errors.append(name+' '+str(width)+': foto rota '+i['src'])
                    for href in data['links']:
                        if href.startswith(('mailto:','tel:','http://','https://','#')):continue
                        local=href.split('?')[0].split('#')[0]
                        if local and not (DIR/local).is_file():errors.append(name+' '+str(width)+': enlace local roto '+href)
                    if width==390:
                        if data['menuVisible']=='none':errors.append(name+': botón móvil no aparece')
                        page.locator('.nav-toggle').click()
                        if not page.locator('.main-nav').evaluate("n => n.classList.contains('open')"):
                            errors.append(name+': botón menú móvil no funciona')
                    if name=='index.html' and len(data['images'])<10:errors.append('Portada incompleta '+str(len(data['images'])))
                    print(json.dumps({'page':name,'viewport':width,'images':len(data['images']),'bad':sum(not i['loaded'] for i in data['images'])}),flush=True)
                except Exception as e:errors.append(name+' '+str(width)+': '+str(e)[:200])
                finally:page.close()
    finally:browser.close()
for e in errors:print('QA_ERROR',e,flush=True)
if errors:raise SystemExit(str(len(errors))+' errores')
print('SERMAFUGAS QA_OK: 12 páginas, 2 resoluciones, logo y fotos comprobados',flush=True)
