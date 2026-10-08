#!/usr/bin/env python3
"""Control de calidad real con navegador Chromium en dos tamaños.
Si falla cualquiera de las páginas propuestas hoy, bloquea su publicación.
No realiza acciones externas ni envía formularios.
"""
import argparse, datetime as dt, json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'automation'/'reports'
PAGES=('index.html','sobre-nosotros.html','contacto.html')

def inspect(page, url, title, checks):
 page.goto(url,wait_until='domcontentloaded',timeout=22000)
 page.wait_for_timeout(1300)
 # Cargar imágenes lazy antes de tomar captura.
 for im in page.locator('img').all():
  try: im.scroll_into_view_if_needed(timeout=1600)
  except Exception:pass
 page.wait_for_timeout(500)
 data=page.evaluate("""() => ({
  width: window.innerWidth,
  scrollWidth: document.documentElement.scrollWidth,
  title: document.title,
  images: Array.from(document.images).map(x=>({src:x.getAttribute('src'), ok:x.complete && x.naturalWidth>0})),
  footer: !!document.querySelector('footer'),
  nav: Array.from(document.querySelectorAll('nav a[href]')).map(a=>a.getAttribute('href')),
  form: !!document.querySelector('form'),
  badCopy: document.body.innerText.includes('Una web para conectar') ||
           document.body.innerText.includes('Conoce nuestra empresa') ||
           document.body.innerText.includes('Una empresa que merece presentarse bien')
 })""")
 if data['scrollWidth']>data['width']+8: checks.append(title+': desbordamiento horizontal '+str(data['scrollWidth'])+'/'+str(data['width']))
 if not data['footer']:checks.append(title+': sin pie de página')
 if data['badCopy']:checks.append(title+': texto comercial impropio')
 if not data['nav']:checks.append(title+': navegación ausente')
 if title.endswith('contacto.html') and not data['form']:checks.append(title+': sin formulario visual')
 for img in data['images']:
  if not img['ok']:checks.append(title+': imagen fallida '+str(img['src'])[:100])
 for href in data['nav']:
  if href.startswith(('#','mailto:','tel:','https://','http://')):continue
  local=href.split('#')[0].split('?')[0]
  if local and local not in PAGES:checks.append(title+': menú con enlace inválido '+local)
 return data

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--demo-test',action='store_true')
 ap.add_argument('--date',default=dt.datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat())
 args=ap.parse_args()
 if args.demo_test:
  demo=ROOT/'auto-demos'/'bonela-integra-s-l-62264'
  folders=[{'name':'Bonela Integra S.L.','folder':'bonela-integra-s-l-62264'}] if demo.is_dir() else []
 else:
  manifest=REPORT/(args.date+'.json')
  if not manifest.exists():raise FileNotFoundError(manifest)
  folders=json.loads(manifest.read_text(encoding='utf-8')).get('entries',[])
 if not folders:
  print('QA: No hay nuevas demos para inspeccionar; sin publicación ficticia')
  return
 problems=[]
 images=0
 with sync_playwright() as pl:
  browser=pl.chromium.launch(headless=True,args=['--no-sandbox'])
  try:
   for c in folders:
    for filename in PAGES:
     f=ROOT/'auto-demos'/c['folder']/filename
     if not f.is_file():
      problems.append(c['name']+'/'+filename+': archivo no encontrado')
      continue
     for view,width,height in (('desktop',1280,800),('mobile',390,844)):
      page=browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
      try:
       checks=[]
       result=inspect(page,f.as_uri(),c['name']+'/'+filename+' / '+view,checks)
       images+=len(result['images'])
       problems+=checks
      except (PWTimeout,Exception) as err:
       problems.append(c['name']+'/'+filename+'/'+view+': error navegador '+type(err).__name__+': '+str(err)[:150])
      finally:page.close()
  finally:browser.close()
 if problems:
  for item in problems:print('QA_ERROR:',item)
  raise RuntimeError(f'QA BLOQUEÓ PUBLICACIÓN: {len(problems)} errores')
 print('QA_OK',len(folders),'empresas, 3 páginas, desktop 1280px y móvil 390px, imágenes revisadas',images)

if __name__=='__main__':main()
