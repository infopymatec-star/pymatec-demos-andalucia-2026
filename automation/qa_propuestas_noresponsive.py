"""QA Chromium de cinco demos; imágenes reales cargadas, menú y responsive."""
import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
SLUGS=['tir-trans-malaga-redisenio','instalaciones-la-roca-redisenio','radiadores-la-vega-redisenio','rotana-gestores-redisenio','promociones-pered-redisenio']
async def inspect(browser,slug,width):
 context=await browser.new_context(viewport={'width':width,'height':844 if width==390 else 800},is_mobile=width==390,device_scale_factor=1)
 page=await context.new_page()
 errs=[]
 try:
  await page.goto((ROOT/'auto-demos'/slug/'index.html').as_uri(),wait_until='domcontentloaded',timeout=26000)
  await page.locator('img').evaluate_all("(els)=>els.forEach(i=>i.loading='eager')")
  await page.wait_for_timeout(2100)
  details=await page.evaluate("""()=>({
   vw:window.innerWidth,sw:document.documentElement.scrollWidth,imgs:[...document.images].map(x=>({url:x.currentSrc||x.src,ok:x.complete&&x.naturalWidth>0,visible:x.getBoundingClientRect().width>40&&x.getBoundingClientRect().height>30})),
   nav:[...document.querySelectorAll('.nav a[href^="#"]')].map(a=>({id:a.hash.slice(1),ok:!!document.getElementById(a.hash.slice(1))})),
   logo:document.querySelector('.brand img')?.naturalWidth||null
  })""")
  if details['sw']>width+9:errs.append('Overflow '+str(details['sw']))
  if len(details['imgs'])<8:errs.append('Insuficientes imágenes: '+str(len(details['imgs'])))
  for i in details['imgs']:
   if not i['ok'] or not i['visible']:errs.append('Imagen no visible '+i['url'])
  for x in details['nav']:
   if not x['ok']:errs.append('Enlace interno roto '+x['id'])
  if width==390:
   b=page.locator('.menu')
   if not await b.is_visible():errs.append('Menú móvil no visible')
   else:
    await b.click()
    if not await page.locator('.nav').evaluate("e=>e.classList.contains('open')"):errs.append('Menú móvil no abre')
  print(json.dumps({'slug':slug,'width':width,'img':len(details['imgs']),'bad':errs},ensure_ascii=False),flush=True)
 except Exception as e: errs.append('Excepción '+str(e)[:200])
 finally:await context.close()
 return errs
async def main():
 allbad=[]
 async with async_playwright() as pw:
  b=await pw.chromium.launch(headless=True,args=['--no-sandbox'])
  for s in SLUGS:
   for width in [1280,390]:
    issues=await inspect(b,s,width)
    allbad.extend([s+' '+str(width)+' '+x for x in issues])
  await b.close()
 for e in allbad:print('QA_ERROR',e,flush=True)
 if allbad:raise RuntimeError(str(len(allbad))+' errores')
 print('QA_OK: 5 webs y 10 vistas, imágenes y navegación válidas',flush=True)
if __name__=='__main__':asyncio.run(main())
