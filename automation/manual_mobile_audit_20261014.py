"""Auditoría de candidatas: captura de pantalla y medidas de navegador real (390 / 1280 px)."""
import json, pathlib, datetime, re
from playwright.sync_api import sync_playwright

SITES = [
    ("carpinteria-sarria-contreras", "https://carpinteriasarriacontreras.es.tl/"),
    ("fontgava", "https://fontgava.es.tl/"),
    ("paco-lopez-multiservicios", "https://pacolopezmultiservicios.es.tl/"),
    ("centro-master-fp", "https://master-fp.es.tl/"),
    ("manolo-peluqueria-caballero", "https://lapeluqueriadelcaballero.es.tl/"),
    ("aluminios-aludecor-marbella", "https://aludecormarbella.es.tl/"),
    ("pipo-park-fuengirola", "https://pipopark.es.tl/"),
    ("carmen-burgos-psicologia", "https://carmenburgos.es.tl/"),
    ("aip-clima-sevilla", "https://aipclima.es.tl/"),
    ("manitas-sevilla-salva", "https://manitassevilla.es.tl/"),
]
OUT = pathlib.Path("automation/reports/2026-10-14-mobile-audit.json")
SHOTS = pathlib.Path("automation/reports/2026-10-14-mobile-shots")
SHOTS.mkdir(parents=True, exist_ok=True)
MEASURE = """() => {
 const w=window.innerWidth, doc=document.documentElement, body=document.body;
 const nodes=[...document.querySelectorAll('header,nav,main,article,table,img,a,section,aside,h1,h2,div')];
 const spills=nodes.filter(el=>{
   const r=el.getBoundingClientRect();
   const s=getComputedStyle(el);
   return r.width>10 && r.height>10 && s.display!=='none' && s.visibility!=='hidden'
    && (r.right>w+20 || r.left < -20);
 }).map(el=>({tag:el.tagName,text:(el.innerText||el.alt||'').replace(/\\s+/g,' ').slice(0,60),left:Math.round(el.getBoundingClientRect().left),right:Math.round(el.getBoundingClientRect().right),width:Math.round(el.getBoundingClientRect().width)})).slice(0,18);
 const images=[...document.images].map(el=>({src:el.currentSrc||el.src,loaded:el.complete && el.naturalWidth>0,naturalWidth:el.naturalWidth})).slice(0,50);
 return {windowWidth:w,scrollWidth:doc.scrollWidth,bodyScrollWidth:body.scrollWidth,hasViewportMeta:!!document.querySelector('meta[name=viewport]'),spillElements:spills,images,headings:[...document.querySelectorAll('h1,h2')].slice(0,8).map(x=>x.innerText.trim()),title:document.title};
}"""
def main():
 report={"run_date":"2026-10-14","auditor":"Playwright Chromium browser", "sites":[]}
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True, args=['--no-sandbox'])
  for slug,url in SITES:
   item={"slug":slug,"url":url,"checks":{}}
   for width in (390,1280):
    page=browser.new_page(viewport={"width":width,"height":800},device_scale_factor=1)
    try:
     response=page.goto(url,wait_until="domcontentloaded",timeout=35000)
     page.wait_for_timeout(2000)
     d=page.evaluate(MEASURE)
     d["httpStatus"]=response.status if response else None
     page.screenshot(path=str(SHOTS/f"{slug}-{width}.png"),full_page=False,timeout=12000)
     item["checks"][str(width)]=d
    except Exception as e:item["checks"][str(width)]={"error":str(e)[:350]}
    finally:page.close()
   m=item["checks"].get("390",{})
   desk=item["checks"].get("1280",{})
   if m.get("httpStatus")==200 and desk.get("httpStatus")==200:
    # Overflow or genuine visible elements beyond mobile viewport is clear evidence.
    item["mobile_overflow_px"]=max(0,m.get("scrollWidth",390)-m.get("windowWidth",390))
    item["mobile_failed"] = item["mobile_overflow_px"] > 30 or len(m.get("spillElements",[]))>2
    item["conclusion"]="nonresponsive_verified" if item["mobile_failed"] else "not_proven_nonresponsive"
   else:item["conclusion"]="inconclusive_site_unavailable"
   report["sites"].append(item)
   print(slug,item["conclusion"],item.get("mobile_overflow_px"),flush=True)
  browser.close()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()
