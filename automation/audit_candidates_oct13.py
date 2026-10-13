"""Auditoría de webs ORIGINALES candidatas, sin publicar ni contactar."""
import json,time
from playwright.sync_api import sync_playwright
sites={
  "Peluquería Luna":"https://peluquerialuna.es.tl/",
  "Naves Málaga":"https://navesmalaga.es.tl/",
  "Desguace El Rocío II":"https://desguaceelrocio.es.tl/",
  "Pádel Almería":"https://padelealmeria.es.tl/",
  "Gil y Gil Pintores":"https://gilygilpintores.es/",
  "AMFS Málaga":"https://www.amfutbolsala.com/",
  "Chemasol":"https://www.chemasol.es/",
  "Acricema":"https://www.acricema.es/",
  "JMG Construcciones":"https://jmgconstrucciones.es/"
}
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,args=["--no-sandbox"])
 for name,url in sites.items():
  result={"name":name,"site":url,"views":[]}
  for width in [1280,390]:
   p=b.new_page(viewport={"width":width,"height":800 if width==1280 else 844},device_scale_factor=1,ignore_https_errors=True)
   try:
    resp=p.goto(url,wait_until="domcontentloaded",timeout=20000)
    p.wait_for_timeout(850)
    r=p.evaluate("""() => {
     const root=document.documentElement;
     const links=[...document.querySelectorAll('nav a, header a, table a, .menu a')].filter(el=> {
        const r=el.getBoundingClientRect(),s=getComputedStyle(el);
        return r.width>8&&r.height>8&&s.visibility!=='hidden'&&s.display!=='none';
     }).slice(0,55);
     const els=[...document.querySelectorAll('h1,h2,p,a,img,input,button,div,table')].filter(el=> {
       const r=el.getBoundingClientRect(),s=getComputedStyle(el);
       return r.width>90&&r.height>14&&s.visibility!=='hidden'&&s.display!=='none'&&r.top<1100&&r.bottom>0;
     });
     const overflow=els.filter(el=>{const r=el.getBoundingClientRect();return r.right>innerWidth+20&&r.left<innerWidth&&r.left>=-40}).slice(0,6).map(e=>({tag:e.tagName,text:e.innerText?.slice(0,55),right:Math.round(e.getBoundingClientRect().right)}));
     return {vw:innerWidth,scroll:root.scrollWidth,body:document.body.scrollWidth,
       meta:document.querySelector('meta[name="viewport"]')?.content||null,
       title:document.title,
       overflow,
       visibleNav:links.length,
       navOffscreen:links.filter(el=>{let r=el.getBoundingClientRect();return r.right>innerWidth+15||r.left < -15}).slice(0,9).map(el=>({text:el.innerText?.slice(0,55),right:Math.round(el.getBoundingClientRect().right)})),
       img:document.images.length};
    }""")
    r.status=resp.status if resp else None
    result["views"].append(r)
   except Exception as e:result["views"].append({"vw":width,"error":str(e)[:150]})
   finally:p.close()
  print("CANDIDATE_AUDIT "+json.dumps(result,ensure_ascii=False),flush=True)
 b.close()
