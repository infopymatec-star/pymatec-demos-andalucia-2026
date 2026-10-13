"""QA de 5 demos del 13 de octubre: Chromium 1280/390, fotos y enlaces."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['malaga-costa-reformas-integrales','cerrajeria-galacho','sistemas-aluminio-las-lagunas','cero21-construcciones','construcciones-pinturas-dajesur']
issues=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
 try:
  for slug in SLUGS:
   path=ROOT/'auto-demos'/slug/'index.html'
   if not path.exists():
    issues.append(slug+': falta index');continue
   for width,height in ((1280,800),(390,844)):
    page=browser.new_page(viewport={'width':width,'height':height})
    try:
     page.goto(path.as_uri(),wait_until='domcontentloaded',timeout=25000)
     for el in page.locator('img').all():
      try:
       el.scroll_into_view_if_needed(timeout=1800)
       el.evaluate("e => e.loading = 'eager'")
      except Exception:pass
     page.wait_for_timeout(2400)
     data=page.evaluate("""() => ({
      width:innerWidth,scroll:document.documentElement.scrollWidth,
      imgs:[...document.images].map(i=>({src:i.src,loaded:i.complete&&i.naturalWidth>0,visible:i.getBoundingClientRect().width>30&&i.getBoundingClientRect().height>30})),
      links:[...document.querySelectorAll('nav a[href^="#"]')].map(a=>({h:a.getAttribute('href'),exists:!!document.getElementById(a.getAttribute('href').slice(1))}))
     })""")
     bad=[x for x in data['imgs'] if not x['loaded'] or not x['visible']]
     if len(data['imgs'])<4:issues.append(slug+' '+str(width)+': menos de 4 fotos')
     if data['scroll']>width+8:issues.append(slug+' '+str(width)+': desbordamiento')
     for img in bad:issues.append(slug+' '+str(width)+': foto rota '+img['src'])
     for a in data['links']:
      if not a['exists']:issues.append(slug+' '+str(width)+': menu roto '+a['h'])
     print(json.dumps({'slug':slug,'view':width,'photos':len(data['imgs']),'bad':len(bad)},ensure_ascii=False),flush=True)
    except Exception as err:issues.append(slug+' '+str(width)+' error '+str(err)[:180])
    finally:page.close()
 finally:browser.close()
for issue in issues:print('QA_ERROR',issue,flush=True)
if issues:raise SystemExit(str(len(issues))+' errores encontrados')
print('QA_OK CINCO DEMOS RESPONSIVE E IMAGENES VERIFICADAS',flush=True)
