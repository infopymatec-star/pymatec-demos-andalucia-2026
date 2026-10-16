"""Auditoría de candidatas NUEVAS (16-10-2026). No publica ni contacta."""
import json
from playwright.sync_api import sync_playwright
sites={
 "Suministros Ríos":"https://suministrosrios.es.tl/",
 "Servicios en Málaga":"https://serviciosenmalaga.es.tl/",
 "Grupo Innovaservicios":"https://innovaservicios.es.tl/",
}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for name,url in sites.items():
  report={"name":name,"original_url":url,"views":[]}
  for width in (390,1280):
   page=browser.new_page(viewport={"width":width,"height":844},device_scale_factor=1,ignore_https_errors=True)
   try:
    response=page.goto(url,wait_until="domcontentloaded",timeout=25000)
    page.wait_for_timeout(1400)
    data=page.evaluate("""() => {
      const v=window.innerWidth,root=document.documentElement;
      const visible=el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>8&&r.height>8};
      const off=[...document.querySelectorAll('a,button,input,textarea')].filter(visible).map(e=>{const r=e.getBoundingClientRect();return {text:(e.innerText||e.getAttribute('aria-label')||'').trim().slice(0,55),left:Math.round(r.left),right:Math.round(r.right),top:Math.round(r.top)}}).filter(x=>x.left>=v||x.right<=0).slice(0,20);
      const clipped=[...document.querySelectorAll('h1,h2,h3,p,table,nav,main,section,aside')].filter(visible).map(e=>{const r=e.getBoundingClientRect();return {tag:e.tagName,text:(e.innerText||'').trim().slice(0,50),left:Math.round(r.left),right:Math.round(r.right)}}).filter(x=>x.right>v+20||x.left < -20).slice(0,12);
      return {viewport:v,scroll_width:root.scrollWidth,body_scroll_width:document.body.scrollWidth,overflow_px:Math.max(root.scrollWidth,document.body.scrollWidth)-v,viewport_meta:document.querySelector('meta[name="viewport"]')?.content||null,clipped,offscreen_controls:off,images:[...document.images].slice(0,25).map(i=>({src:i.currentSrc?.slice(0,140),ok:i.complete&&i.naturalWidth>0}))};
    }""")
    data["http_status"]=response.status if response else None
    report["views"].append(data)
   except Exception as ex:report["views"].append({"viewport":width,"error":str(ex)[:240]})
   finally:page.close()
  print("AUDIT_20261016 "+json.dumps(report,ensure_ascii=False),flush=True)
 browser.close()
