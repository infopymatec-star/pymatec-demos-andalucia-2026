#!/usr/bin/env python3
"""Auditoría REAL en Chromium, 10 demos publicadas, móvil/escritorio."""
import json, os, time
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

SLUGS = ["carpinteria-sarria-contreras","fontgava","paco-lopez-multiservicios",
"centro-master-fp","aludecor-marbella","manolo-peluqueria-caballero",
"multiservicios-monge","ingenieria-del-olivar","construcciones-ceyve","pulidos-fc","talleres-luis-marin"]
BASE = "https://infopymatec-star.github.io/pymatec-demos-andalucia-2026/auto-demos/"
OUT = Path(__file__).resolve().parents[1]/"automation"/"reports"/"qa-redisenos-10.json"
OUT.parent.mkdir(parents=True,exist_ok=True)
report={"date":datetime.now(timezone.utc).isoformat(),"status":"pending","checks":[],"errors":[]}

with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 try:
  for slug in SLUGS:
   for view,width in [("mobile",390),("desktop",1280)]:
    label=f"{slug}/{view}"
    record={"slug":slug,"viewport":width,"url":BASE+slug+"/","status":"pending","errors":[]}
    for attempt in range(3):
     context=browser.new_context(viewport={"width":width,"height":844 if width==390 else 800},
       device_scale_factor=1,ignore_https_errors=False)
     page=context.new_page()
     try:
      resp=page.goto(BASE+slug+"/",wait_until="domcontentloaded",timeout=45000)
      if not resp or resp.status>=400:raise RuntimeError(f"HTTP {resp.status if resp else 'no response'}")
      page.locator("h1").wait_for(timeout=8000)
      page.wait_for_timeout(1600)
      checks=page.evaluate("""() => ({
        viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
        pageTitle:document.title,h1:document.querySelector('h1')?.innerText,
        heroWidth:document.querySelector('h1')?.getBoundingClientRect().width,
        css:!![...document.styleSheets].find(s=>(s.href||'').includes('studio-v2.css')),
        cssWidth:getComputedStyle(document.querySelector('.wrap')).maxWidth,
        services:document.querySelectorAll('.service-card').length,
        photos:[...document.images].map(i=>({src:i.currentSrc||i.src,loaded:i.complete&&i.naturalWidth>0,
          naturalWidth:i.naturalWidth,width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})),
        mail:[...document.querySelectorAll('a[href^="mailto:"]')].map(a=>a.href),
        phone:[...document.querySelectorAll('a[href^="tel:"]')].map(a=>a.href),
        links:[...document.querySelectorAll('.menu a[href]')].map(a=>a.getAttribute('href')),
        sourceWords:/Fuentes p[úu]blicas|Verificaci[óo]n de informaci[óo]n|Fuentes consultadas/i.test(document.body.innerText),
        disclaimer:document.body.innerText.includes('Propuesta visual no oficial'),
        mobileMenu:!!document.querySelector('details.mobile-menu')
      })""")
      errs=[]
      if checks["scrollWidth"]>width+3:errs.append(f"scroll horizontal {checks['scrollWidth']}>{width}")
      if not checks["css"]:errs.append("No se cargó hoja de estilos studio-v2.css")
      if not checks["h1"]:errs.append("Cabecera ausente")
      if checks["services"]<3:errs.append("Menos de 3 servicios")
      if not checks["photos"]:errs.append("No hay fotografía de portada")
      for photo in checks["photos"]:
       if not photo["loaded"]:errs.append("Foto sin cargar "+photo["src"][:130])
       if photo["width"]<100 or photo["height"]<100:errs.append("Fotografía no visible")
      if not checks["mail"] or not checks["phone"]:errs.append("Falta contacto real")
      if not checks["disclaimer"]:errs.append("Falta aviso de demo no oficial")
      if checks["sourceWords"]:errs.append("Exposición indebida de auditoría de fuentes")
      for href in checks["links"]:
       if href.startswith("#") and not page.locator(href).count():errs.append("Ancla ausente "+href)
      if view=="mobile":
       page.locator("details.mobile-menu summary").click(timeout=4000)
       if not page.locator("details.mobile-menu[open] .mob-links a").count():errs.append("Menú móvil no abre")
      record.update({"status":"pass" if not errs else "fail","metrics":checks,"errors":errs})
      page.screenshot(path=str(OUT.parent/f"qa-{slug}-{view}.png"),full_page=True,timeout=30000)
      break
     except Exception as ex:
      record.update({"status":"error","errors":[type(ex).__name__+": "+str(ex)[:240]]})
      if attempt<2:time.sleep(7)
     finally:
      context.close()
    report["checks"].append(record)
    report["errors"].extend([label+" "+e for e in record["errors"]])
 finally:browser.close()
report["status"]="pass" if len(report["checks"])==20 and not report["errors"] else "fail"
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("RESULT",report["status"],"checks",len(report["checks"]),"errors",len(report["errors"]))
for e in report["errors"]:print("QA_FAIL:",e)
raise SystemExit(0 if report["status"]=="pass" else 1)
