#!/usr/bin/env python3
"""Auditoría EXCLUSIVAMENTE informativa de webs originales en dispositivo móvil."""
import asyncio, json, re, datetime
from pathlib import Path
from playwright.async_api import async_playwright
SITES=[
("TIR TRANS MALAGA","https://www.tirtrans.es/"),
("Aluminios Racero","https://aluminiosracero.com/"),
("Roesca Carpintería Metálica","https://www.roesca.com/"),
("KeyStation","https://keystation.es/"),
("Parquet Coema","https://www.parquetmalaga.net/"),
("Sicilia Hermanos","https://www.puertasmetalicasmalaga.es/"),
("Ibérica de Andamios","https://www.alquilerandamiosmalaga.com/"),
("MELA sistemas contra incendios","https://www.sistemascontraincendiomalaga.es/"),
("Pinturas Gil y Gil","https://gilygilpintores.es/"),
("Rafael Bermúdez Abogado","https://www.rafaelbermudezabogado.es/"),
("Los Pintores Decorativos","https://lospintoresdecorativos.jimdofree.com/"),
("Asociación Malagueña Fútbol Sala","https://www.amfutbolsala.com/"),
("Tecnomampara","https://tecnomampara.es/"),
("SIER Tecnología","https://www.sier.es/"),
("OFIBURO","https://ofiburo.com/"),
("Axar Parquet","https://www.axarparquet.es/"),
("Grupo Lagar","https://www.grupolagar.es/"),
("Toldos Luz y Color","https://toldosluzycolor.es/"),
("Toldos Río Mar","https://riomarsystem.com/"),
("Muebles y Persianas Salmasol","https://salmasol.com/"),
("Aluminios Chemasol","https://www.chemasol.es/"),
("Acricema","https://www.acricema.es/"),
("JMG Construcciones","https://jmgconstrucciones.es/"),
("Pinturas Sola","https://www.pinturassola.com/"),
("Muebles Almacenes Remar","https://www.mueblesremar.es/"),
("Toldos La Costa","https://www.toldoslacosta.com/"),
("Limpiezas Costa del Sol","https://www.limpiezascostadelsol.es/"),
("Persianas Roldán","https://www.persianasroldan.com/"),
("Empresa Ronda Cerrajeros","https://www.cerrajeriaronda.es/"),
]
SITES.extend([
 ("Miguel y Porcel SL","https://miguelyporcelsl.es.tl/"),
 ("Radiadores La Vega","https://radiadoreslavega.es.tl/"),
 ("Rotana Gestores","https://rotanagestores.es.tl/"),
 ("Instalaciones La Roca","https://instalacioneslaroca.es.tl/"),
 ("Promociones Pered","https://promocionespered.es.tl/"),
 ("Peluquería Luna","https://peluquerialuna.es.tl/"),
])
JS="""() => {
 const els=[...document.querySelectorAll('body *')].filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>50&&r.height>10});
 const offenders=els.filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+15||r.left< -20}).slice(0,8).map(e=>({tag:e.tagName,cl:String(e.className).slice(0,70),right:Math.round(e.getBoundingClientRect().right),width:Math.round(e.getBoundingClientRect().width)}));
 const links=[...document.querySelectorAll('nav a, header a')].filter(e=>{let r=e.getBoundingClientRect();return r.width>10&&r.height>10}).length;
 const tiny=[...document.querySelectorAll('p,a,li,h1,h2,button')].filter(e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>10&&r.height>5&&r.top>0&&r.top<800&&parseFloat(s.fontSize)<11}).length;
 return {innerWidth:innerWidth,viewport:visualViewport?.width||null,docWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,meta:document.querySelector('meta[name=viewport]')?.content||null,offenders,visibleNavLinks:links,tinyTextElements:tiny,title:document.title,images:[...document.images].length,
 logoCandidates:[...document.querySelectorAll('header img,.logo img,img[class*=logo],#logo img')].slice(0,5).map(i=>i.currentSrc)};
}"""
async def check(browser, sem, name,url):
 async with sem:
  row={'name':name,'url':url,'checked_at':'2026-10-13'}
  for form in ('desktop','mobile'):
   p=None
   try:
    ctx=await browser.new_context(viewport={'width':1280 if form=='desktop' else 390,'height':800 if form=='desktop' else 844},is_mobile=form=='mobile',device_scale_factor=1,has_touch=form=='mobile',ignore_https_errors=True,user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1' if form=='mobile' else None)
    p=await ctx.new_page()
    try: await p.goto(url,wait_until='domcontentloaded',timeout=15500)
    except Exception: pass
    await p.wait_for_timeout(900)
    row[form]=await p.evaluate(JS)
    row[form]['finalUrl']=p.url
    await ctx.close()
   except Exception as e:
    row[form]={'error':str(e)[:170]}
    try: await p.context.close()
    except Exception: pass
  m=row.get('mobile',{}); d=row.get('desktop',{})
  if m.get('innerWidth'):
   causes=[]
   if m['innerWidth']>425:causes.append('La anchura CSS móvil es '+str(m['innerWidth'])+'px para dispositivo de 390px (meta viewport fija o ausente)')
   if m.get('docWidth',0)>m.get('innerWidth',390)+15:causes.append('Desbordamiento horizontal móvil: '+str(m['docWidth'])+'px frente a '+str(m['innerWidth'])+'px')
   if len(m.get('offenders',[]))>1:causes.append('Elementos fuera de pantalla: '+str(len(m['offenders'])))
   row['mobile_fail_evidence']=causes
   row['confirmed_nonresponsive']=bool(causes) and bool(d.get('innerWidth'))
  else: row['confirmed_nonresponsive']=False
  return row
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'])
  sem=asyncio.Semaphore(6)
  data=await asyncio.gather(*[check(browser,sem,name,url) for name,url in SITES])
  await browser.close()
 output=Path('automation/reports/auditoria-originales-2026-10-13.json')
 output.parent.mkdir(parents=True,exist_ok=True)
 output.write_text(json.dumps({'date':'2026-10-13','note':'Comprobación browser; solo clasificar no responsive con evidencia en 390 y 1280','results':data},ensure_ascii=False,indent=2),encoding='utf-8')
 for d in data:
  print(d['name'],'FAIL' if d['confirmed_nonresponsive'] else 'NO_CONFIRMADO',d.get('mobile_fail_evidence'),(d.get('mobile') or {}).get('error',''),flush=True)
 print('RESULTADOS',sum(x['confirmed_nonresponsive'] for x in data),'de',len(data),flush=True)
if __name__=='__main__':asyncio.run(main())
