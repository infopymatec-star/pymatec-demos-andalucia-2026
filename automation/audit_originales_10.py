#!/usr/bin/env python3
"""Prueba móvil objetiva de webs ORIGINALES, sin inferir fallos de antigüedad."""
import json, time
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]/"automation"/"reports"
BASE.mkdir(parents=True,exist_ok=True)
CASES=[
("Carpintería Sarria Contreras","https://carpinteriasarriacontreras.es.tl/"),
("Fontgava","https://fontgava.es.tl/"),
("Paco López Multiservicios","https://pacolopezmultiservicios.es.tl/"),
("Centro Máster FP","https://master-fp.es.tl/"),
("Aludecor Marbella","https://aludecormarbella.es.tl/"),
("Manolo La Peluquería del Caballero","https://lapeluqueriadelcaballero.es.tl/"),
("Multiservicios Monge","https://multiserviciosmonge.es.tl/"),
("Ingeniería del Olivar","https://ingenieriadelolivar.es.tl/"),
("Construcciones CEYVE","https://ceyve.es.tl/"),
("Pulidos F.C.","https://pulidosfc.es.tl/"),
("Talleres Luis Marín","https://talleresluismarin.es.tl/")
]
report={"date":datetime.now(timezone.utc).isoformat(),"results":[],"total":len(CASES)}
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
 try:
  for name,url in CASES:
   item={"name":name,"url":url,"mobileStatus":"not_verified"}
   page=browser.new_page(viewport={"width":390,"height":844},device_scale_factor=1,is_mobile=True,has_touch=True)
   try:
    res=page.goto(url,wait_until="domcontentloaded",timeout=33000)
    page.wait_for_timeout(1000)
    stats=page.evaluate("""() => {
      const rects=[...document.querySelectorAll('a')].filter(a=>getComputedStyle(a).display!=='none')
      .slice(0,70).map(a=>({t:a.textContent.trim().slice(0,45),left:Math.round(a.getBoundingClientRect().left),right:Math.round(a.getBoundingClientRect().right)}));
      const text=[...document.querySelectorAll('h1,h2,p,td')].filter(x=>getComputedStyle(x).display!=='none')
      .slice(0,90).map(x=>({tag:x.tagName,left:Math.round(x.getBoundingClientRect().left),right:Math.round(x.getBoundingClientRect().right)}));
      return {innerWidth:innerWidth,visualWidth:visualViewport.width,clientWidth:document.documentElement.clientWidth,
      scrollWidth:document.documentElement.scrollWidth,bodyScroll:document.body.scrollWidth,
      viewportMeta:document.querySelector('meta[name=viewport]')?.content||null,
      linksOffscreen:rects.filter(r=>r.right>390+10||r.left < -10).slice(0,12),
      textOffscreen:text.filter(r=>r.right>390+10||r.left < -10).slice(0,12),
      anchors:rects.length};
    }""")
    defects=[]
    if stats["scrollWidth"]>max(stats["innerWidth"],390)+12: defects.append(f"document.scrollWidth={stats['scrollWidth']} sobre innerWidth={stats['innerWidth']}")
    if stats["innerWidth"]>440: defects.append(f"layout viewport {stats['innerWidth']}px en dispositivo de 390px (reescala)")
    if len(stats["linksOffscreen"])>=2: defects.append(f"{len(stats['linksOffscreen'])} enlaces relevantes fuera de 390px")
    if len(stats["textOffscreen"])>=4: defects.append(f"{len(stats['textOffscreen'])} elementos de texto fuera de 390px")
    item.update({"httpStatus":res.status if res else None,"mobileStatus":"no_responsive_verified" if defects else "not_proven_nonresponsive",
      "evidence":defects,"metrics":stats})
    page.screenshot(path=str(BASE/("original-"+url.split("//")[1].split("/")[0]+".png")),full_page=True,timeout=18000)
   except Exception as ex:
    item.update({"mobileStatus":"unknown_error","error":str(ex)[:180]})
   finally:page.close()
   report["results"].append(item)
 finally: browser.close()
report["confirmedCount"]=sum(x["mobileStatus"]=="no_responsive_verified" for x in report["results"])
(BASE/"audit-originales-10.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print("ORIGINAL_AUDIT",report["confirmedCount"],"/",len(CASES))
for x in report["results"]:print(x["name"],x["mobileStatus"],x.get("evidence",[]),x.get("error",""))
