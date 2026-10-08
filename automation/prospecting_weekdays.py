#!/usr/bin/env python3
"""Pymatec · captación responsable (laborables 08:37 Europe/Madrid).
Busca candidatos, contrasta evidencias, publica solo maquetas validadas,
prepara correos SIN enviarlos y mantiene histórico de exclusiones.
No promete cinco resultados cuando las fuentes gratuitas no los acreditan.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, html, json, os, re, time, unicodedata
from pathlib import Path
from urllib.parse import urlparse, quote, urljoin
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
from site_pages import make_pages
from free_daily import slugify, public_site, domain, valid_email, extract_email, extract_logo, CRAFTS, gmail_compose

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'auto-demos'
STATE=ROOT/'automation'/'seen.json'
REPORT=ROOT/'automation'/'reports'
EXCLUSIONS=ROOT/'automation'/'excluded_companies.json'
SITE_BASE='https://infopymatec-star.github.io/pymatec-demos-andalucia-2026/auto-demos/'
HEADERS={'User-Agent':'Pymatec-research/2.0 (contact: info.pymatec@gmail.com)','Accept-Language':'es-ES,es;q=0.9'}
TOWN=[
 ('Málaga',36.7213,-4.4214),('Torremolinos',36.6226,-4.4990),
 ('Benalmádena',36.5988,-4.5168),('Fuengirola',36.5391,-4.6243),
 ('Mijas',36.5958,-4.6373),('Alhaurín de la Torre',36.6640,-4.5615),
 ('Alhaurín el Grande',36.6458,-4.6877),('Coín',36.6591,-4.7567),
 ('Cártama',36.7116,-4.6301),('Rincón de la Victoria',36.7164,-4.2812),
 ('Vélez-Málaga',36.7819,-4.1005),('Nerja',36.7451,-3.8767),
 ('Marbella',36.5099,-4.8858),('Estepona',36.4274,-5.1459),
 ('Antequera',37.0194,-4.5607),('Ronda',36.7423,-5.1671),
 ('Archidona',37.0962,-4.3885),('Álora',36.8233,-4.7057),
]
SECTORS={
 'electrician','plumber','carpenter','painter','roofer','gardener','tiler',
 'glaziery','floorer','hvac','handyman'
}
ECOM=('añadir al carrito','add to cart','woocommerce-cart','shopify-payment-button','finalizar compra','cart-items')
BAD_CONTACT=('topdigital','tdconsulting','top-digital')
COMMON_BAD=('facebook.com','instagram.com','linkedin.com','wixsite.com','google.com','business.site','wa.me')
NO_MAIL="No disponible"
def norm(s):
 return unicodedata.normalize('NFKD',str(s or '')).encode('ascii','ignore').decode('ascii').lower()
def banned(s,config):
 n=norm(s).replace(' ','').replace('-','')
 return any(norm(word).replace(' ','').replace('-','') in n for word in config['fragments'] if len(word)>2)
def settings():
 default={'fragments':['topdigital','tdconsulting','top digital','grupo topdigital'],
          'domains':['topdigital.es','tdconsulting.es','grupotopdigital.es'],
          'emails':[],'names':[],'previously_contacted':[]}
 try:
  raw=json.loads(EXCLUSIONS.read_text(encoding='utf-8'))
  for k in default: default[k]=list(dict.fromkeys(default[k]+list(raw.get(k,[]))))
 except (FileNotFoundError,ValueError,TypeError): pass
 return default
def banned_candidate(c,cfg):
 values=[c.get(k,'') for k in ('name','website','domain','email','about','phone','address')]
 if any(banned(v,cfg) for v in values): return True
 if domain(c.get('website','')) in cfg['domains']: return True
 if any(norm(c.get('name'))==norm(x) for x in cfg['names']+cfg['previously_contacted']): return True
 if c.get('email','').lower() in cfg['emails']: return True
 return False
def prior_history():
 try: prev=json.loads(STATE.read_text(encoding='utf-8'))
 except (FileNotFoundError,ValueError): prev={}
 # Preserve the original leads and explicit demos from earlier work.
 prev.setdefault('domains',[])
 prev.setdefault('names',[])
 prev.setdefault('osm_ids',[])
 prev.setdefault('emails',[])
 prev.setdefault('events',[])
 for dom in ('laureanoramos.es','logarze.es','instalacionesmesa.com',
   'carpinterosjaen.com','oryxobrasyservicios.com','bonelaintegra.com'):
  if dom not in prev['domains']:prev['domains'].append(dom)
 return prev
def known(c,state):
 for k,field in (('domain','domains'),('osm_id','osm_ids'),('email','emails')):
  if c.get(k) and norm(c[k]) in set(norm(x) for x in state[field]): return True
 if c.get('name') and norm(c['name']) in set(norm(x) for x in state['names']):return True
 return False
def req(url,timeout=12):
 u=public_site(url)
 if not u: raise ValueError('URL no pública')
 r=requests.get(u,headers=HEADERS,timeout=timeout,allow_redirects=True)
 r.raise_for_status()
 if len(r.content)>1_500_000 or not public_site(r.url):raise ValueError('contenido no aceptado')
 if 'text/html' not in r.headers.get('content-type','text/html'):raise ValueError('no es HTML')
 return r
def osm(city):
 city_name,lat,lon=city
 pattern='|'.join(re.escape(x) for x in sorted(SECTORS))
 query=f'''[out:json][timeout:24];nwr(around:8000,{lat},{lon})["craft"~"^({pattern})$"]["name"];out tags center 180;'''
 problems=[]
 for endpoint in ('https://overpass.kumi.systems/api/interpreter','https://overpass-api.de/api/interpreter'):
  try:
   r=requests.post(endpoint,headers=HEADERS,data={'data':query},timeout=40)
   r.raise_for_status()
   return (r.json().get('elements') or []),problems
  except Exception as e: problems.append('Fuente pública temporalmente no accesible: '+type(e).__name__)
 return [],problems
def address_from_tags(tags,city):
 line=', '.join(x for x in [tags.get('addr:street'),tags.get('addr:housenumber')] if x)
 place=tags.get('addr:city') or city
 return ', '.join(x for x in [line,place,'Málaga'] if x)
def candidate(row,city,cfg,prev):
 tags=row.get('tags') or {}
 craft=tags.get('craft','')
 name=(tags.get('name') or '').strip()
 if craft not in SECTORS or not name or len(name)>100: return
 url=public_site(tags.get('website') or tags.get('contact:website') or '')
 email=(tags.get('contact:email') or tags.get('email') or '').strip().lower()
 if email and not valid_email(email): email=''
 phone=(tags.get('contact:phone') or tags.get('phone') or '').strip()
 ident=str(row.get('type',''))+':'+str(row.get('id',''))
 out={'name':name,'craft':craft,'website':url or '','domain':domain(url) if url else '',
   'email':email,'phone':phone[:40],'osm_id':ident,
   'address':address_from_tags(tags,city),'address_confirmed':bool(tags.get('addr:street') and tags.get('addr:housenumber')),'city':city,
   'source':'https://www.openstreetmap.org/'+str(row.get('type','node'))+'/'+str(row.get('id','')),
   'group':'con-web' if url else 'sin-web-localizada'}
 if banned_candidate(out,cfg) or known(out,prev):return
 return out
def bad_shop(soup):
 text=soup.get_text(' ',strip=True).lower()[:50000]
 return any(word in text for word in ECOM)
def historical_signals(soup,response):
 raw=response.text[:220000].lower()
 text=soup.get_text(' ',strip=True).lower()
 reasons=[]
 if not soup.select_one('meta[name="viewport"]'): reasons.append('No declara meta viewport móvil')
 if '<table' in raw and ('width="900"' in raw or 'width="1000"' in raw):reasons.append('Diseño rígido de tablas detectado')
 if re.search(r'<font\b|<marquee\b',raw): reasons.append('Etiquetas HTML obsoletas detectadas')
 if re.search(r'generator.{0,35}wordpress\s+[1-4]\.',raw): reasons.append('Generador CMS antiguo declarado')
 if re.search(r'\b(?:copyright|©)\s*(?:201[0-9]|202[0-1])\b',text): reasons.append('Copyright visible sin actualización desde 2021 o antes')
 if any(('width="'+str(w)+'"') in raw for w in (900,960,1000,1024)): reasons.append('Ancho HTML fijo detectado')
 if response.url.startswith('http://'):reasons.append('Sitio servido sin HTTPS')
 return reasons
def extract(c,cfg):
 rr=req(c['website'])
 soup=BeautifulSoup(rr.text,'html.parser')
 if bad_shop(soup):return None
 if not soup.title or not soup.get_text(' ',strip=True):return None
 reasons=historical_signals(soup,rr)
 # No se etiqueta "anticuada" una web solo por opiniones estéticas.
 if not reasons:return None
 mail=extract_email(soup)
 # Contacto institucional verificable en web, no inventado.
 if not mail:
  for a in soup.select('a[href]'):
   href=a.get('href','')
   if not any(k in (href+' '+a.get_text(' ',strip=True)).lower() for k in ('contact','contacto','contactar')):continue
   u=public_site(urljoin(rr.url,href))
   if not u or domain(u)!=domain(rr.url):continue
   try:
    mail=extract_email(BeautifulSoup(req(u,7).text,'html.parser'))
    if mail:break
   except (requests.RequestException,ValueError):pass
 if not mail:mail=c['email']
 if mail and not valid_email(mail):mail=''
 phone_el=soup.select_one('a[href^="tel:"]')
 phone=(phone_el.get('href','')[4:] if phone_el else c['phone']).strip()[:40]
 if not phone and not mail:return None
 # Reject disallowed relations even if they appear in the website footer.
 if banned(rr.url,cfg) or banned(c['name'],cfg) or banned(mail,cfg):return None
 visible=norm(soup.get_text(' ',strip=True)[:18000])
 if any(norm(term).replace(' ','') in visible.replace(' ','') for term in ('diseñado por tdconsulting','desarrollado por topdigital','grupo topdigital','desarrollado por tdconsulting')):return None
 cleanSoup=BeautifulSoup(rr.text,'html.parser')
 for el in cleanSoup(['script','style','noscript','template']):el.decompose()
 paragraphs=[p.get_text(' ',strip=True) for p in cleanSoup.find_all('p') if 90<=len(p.get_text(' ',strip=True))<=500]
 about=next((p for p in paragraphs if any(t in norm(p) for t in ('empresa','especialist','servicios','ofrecemos','instalacion','trayectoria'))), '')
 # For a credible demo demand at least a contact and 1 adequate description.
 if not about:return None
 logo=extract_logo(soup,rr.url)
 theme=soup.select_one('meta[name="theme-color"]')
 color=(theme.get('content') if theme else '') or ''
 if not re.fullmatch(r'#[0-9a-fA-F]{6}',color):color=CRAFTS[c['craft']][1]
 return {**c,'email':mail,'phone':phone,'logo':logo,'color':color,'verified_url':rr.url,
  'about':about[:480],'activity':CRAFTS[c['craft']][0],'services':[CRAFTS[c['craft']][0]],
  'website_signals':reasons,'group':'web-mejorable',
  'footer_description':about[:180],
  'hero_title':CRAFTS[c['craft']][0]+' en '+c['city']+'.',
  'hero_subtitle':about[:220],
  'services_intro':'Contacta para conocer los servicios y solicitar información sobre tu proyecto.'}
def checked_no_website(c):
 """Do not claim absence merely because an OSM item lacks website=."""
 if c['website'] or not c['email'] or not c['phone'] or not c.get('address_confirmed'):
  return False,'Faltan evidencias independientes o datos de contacto'
 # Un motor público puede no responder; entonces se descarta, no se inventa el resultado.
 try:
  query='"'+c['name']+'" "'+c['city']+'" página web'
  r=requests.get('https://www.google.com/search',params={'q':query,'num':10},headers=HEADERS,timeout=10)
  r.raise_for_status()
  body=BeautifulSoup(r.text,'html.parser').get_text(' ',strip=True).lower()
  if len(body)<350 or 'unusual traffic' in body or 'captcha' in body:return False,'Búsqueda no verificable'
  # Exigir segundo indicio independiente: identidad, localidad y email.
  normalized=norm(body)
  if norm(c['name']) not in normalized or norm(c['city']) not in normalized:
   return False,'No se corrobora identidad y localidad en la segunda fuente'
  if c['email'].lower() not in body:
   return False,'No se corrobora el correo corporativo en una segunda fuente'
  # Si hay enlace que parece web oficial, no se clasifica como sin web.
  excluded_domains=('google.','facebook.','instagram.','linkedin.','paginasamarillas.',
    'empresite.','einforma.','axesor.','infoempresa.','cylex.','mapquest.','openstreetmap.')
  links=BeautifulSoup(r.text,'html.parser').select('a[href]')
  company_tokens=[x for x in norm(c['name']).split() if len(x)>=5 and x not in ('servicios','empresa','construcciones','mantenimiento')]
  for a in links[:75]:
   href=a.get('href','')
   h=urlparse(href).hostname or ''
   if not h or any(term in h for term in excluded_domains):continue
   visible_link=norm(a.get_text(' ',strip=True))
   if company_tokens and all(x in visible_link for x in company_tokens[:2]):
    return False,'Se localiza enlace web posiblemente oficial: requiere investigación manual'
  return True,'Sin web oficial identificable en ficha y búsqueda limitada; ausencia no demostrable'
 except Exception:return False,'Búsqueda de contraste no disponible'
def info_without_website(c):
 # Se debe evitar afirmar servicios concretos, acreditaciones o antigüedad no contrastadas.
 sector=CRAFTS[c['craft']]
 name=c['name']
 return {**c,'verified_url':'','logo':None,'color':sector[1],
  'about':name+' figura en un registro público con actividad de '+sector[0].lower()+
    ' en '+c['city']+'. Consulta las condiciones y disponibilidad directamente con la empresa.',
  'activity':sector[0],'services':[sector[0]],
  'footer_description':sector[0]+' · '+c['city'],
  'hero_title':sector[0]+' en '+c['city']+'.',
  'hero_subtitle':'Contacta para consultar el servicio y solicitar información.',
  'group':'sin-web-localizada'}
def verify_static(pages,company):
 expected={'index.html','sobre-nosotros.html','contacto.html'}
 if set(pages)!=expected:raise ValueError('Página obligatoria ausente')
 for filename,content in pages.items():
  soup=BeautifulSoup(content,'html.parser')
  if not soup.title or not soup.select_one('footer') or not soup.select_one('nav'):raise ValueError('Estructura incompleta')
  if company['name'] not in content:raise ValueError('Nombre empresa incorrecto')
  if company.get('email') and company['email'] not in content:raise ValueError('Email no visible')
  for a in soup.select('a[href]'):
   href=a.get('href','')
   if href.startswith(('#','mailto:','tel:','https:')):continue
   fname=href.split('#')[0].split('?')[0]
   if fname and fname not in expected:raise ValueError('Enlace local no válido: '+fname)
  for img in soup.select('img'):
   if not img.get('alt'):raise ValueError('Imagen sin alt')
  if any(phrase in content for phrase in ('Una empresa que merece presentarse bien','Una web para conectar','Una web más clara')):raise ValueError('Texto impropio')
 if 'id="sobre-nosotros"' in pages['index.html']:raise ValueError('Sobre nosotros duplicado en Inicio')
 if 'Formulario de demostración' not in pages['contacto.html']:raise ValueError('Formulario no declarado demo')
def create_mail(c,link):
 subject='Propuesta visual para la web'
 # Describir mejoras, sin hacer reproches tecnológicos ni atribuir fallos sin evidencia.
 mapping={
  'No declara meta viewport móvil':'mejor presentación y navegación en dispositivos móviles',
  'Diseño rígido de tablas detectado':'una estructura más limpia y flexible',
  'Etiquetas HTML obsoletas detectadas':'un diseño más actual y accesible',
  'Generador CMS antiguo declarado':'un sitio mejor preparado para navegadores actuales',
  'Copyright visible sin actualización desde 2021 o antes':'contenidos e información corporativa revisados',
  'Ancho HTML fijo detectado':'mejor adaptación a diferentes tamaños de pantalla',
  'Sitio servido sin HTTPS':'una configuración segura con HTTPS en la versión definitiva'
 }
 improvements=[mapping.get(x,'una estructura más clara de servicios y contacto') for x in c.get('website_signals',[])[:2]]
 if not improvements: improvements=['una mejor presentación de los servicios y un acceso sencillo al contacto']
 intro=('He revisado vuestra web actual y su información pública.'
        if c['group']=='web-mejorable' else
        'He revisado la información pública disponible sobre vuestra empresa.')
 params={
  'INTRO':intro,
  'EMPRESA':c['name'],
  'ACTIVIDAD':c['activity'].lower(),
  'MEJORAS':'; '.join(improvements),
  'ENLACE_WEB':link
 }
 txt=(ROOT/'automation'/'email_tipo.md').read_text(encoding='utf-8')
 for key,value in params.items():
  if txt.count('{{'+key+'}}')!=1:raise ValueError('Plantilla incorrecta: '+key)
  txt=txt.replace('{{'+key+'}}',value)
 if '{{' in txt:raise ValueError('Marcador sin resolver en propuesta')
 plain=txt.replace('**[Enlace web]('+link+')**',link).replace('**','')
 return subject,txt,gmail_compose(c['email'],subject,plain) if c.get('email') else ''

def make_report(day,city,rows,notes,scanned):
 counts={'sin-web-localizada':sum(x['group']=='sin-web-localizada' for x in rows),
   'web-mejorable':sum(x['group']=='web-mejorable' for x in rows)}
 lines=[f'# Pymatec · informe diario {day}', '',
  f'**Ámbito:** {city}, Málaga. **Objetivo:** 5 empresas (2 sin web localizada + 3 webs mejorables).',
  f'**Resultado verificado:** {len(rows)} empresas. Webs mejorables: {counts["web-mejorable"]}. Sin web localizada: {counts["sin-web-localizada"]}.',
  f'**Candidatas revisadas:** {scanned}. **Correo comercial enviado:** 0.',
  '**Nota:** inicio previsto 08:37, envío del resumen al finalizar (no simultáneo a la búsqueda).',
  '**Exclusiones permanentes:** Grupo TOPdigital, TDconsulting y coincidencias en registros de exclusión.',
  '']
 for i,c in enumerate(rows,1):
  lines+= [f'## {i}. {c["name"]}',f'- Actividad: {c["activity"]}',
   f'- Localidad: {c["city"]}',f'- Web actual: {c["verified_url"] if c.get("verified_url") else "Sin sitio web oficial localizado; ausencia no demostrable"}',
   f'- Nueva propuesta: {c["demo_url"]}',f'- Email verificado: {c.get("email") or NO_MAIL}',
   '- Estado del correo comercial: **preparado, no enviado; revisar autorización legal**',
   f'- Evidencias: {", ".join(c.get("website_signals",[])) or c.get("site_evidence","Referencia en registro público verificado")}',
   f'- Fuente principal: {c.get("verified_url") or c["source"]}', '']
 if not rows:lines +=['No se ha completado una propuesta: no hubo fuentes suficientes para una selección fiable.','']
 if notes:lines+=['## Limitaciones']+[f'- {n}' for n in notes]+['']
 lines+=['## Control editorial y legal',
  '- Todas las webs publicadas han superado pruebas locales de estructura, contenido y enlaces.',
  '- No se presenta como "web antigua" una página sin señales objetivas.',
  '- Ausencia de web no implica certeza; requiere una búsqueda limitada y datos contrastados.',
  '- Los formularios de las demos **NO envían** información.',
  '- La publicación por GitHub Pages necesita verificación HTTP adicional antes de dar por confirmado su acceso público.',
  '- Ningún correo comercial se envía automáticamente. Artículo 21 LSSI: https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758#a21',
  '']
 return '\n'.join(lines)
def write_manifest(day,entries,notes,city):
 REPORT.mkdir(parents=True,exist_ok=True)
 data={'date':day,'city':city,'target':5,'count':len(entries),'status':'generated_pending_publication',
  'entries':[{k:v for k,v in e.items() if k in (
   'name','activity','city','website','verified_url','email','group','demo_url','website_signals','site_evidence',
   'osm_id','source','folder')} for e in entries],
  'limitations':notes,'commercial_emails_sent':0,'summary_email_sent':False}
 (REPORT/(day+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def save_state(prev,rows,day):
 for c in rows:
  for k,field in (('domain','domains'),('name','names'),('osm_id','osm_ids'),('email','emails')):
   value=c.get(k)
   if value and value not in prev[field]:prev[field].append(value)
  prev['events'].append({'date':day,'name':c['name'],'group':c['group'],'link':c['demo_url'],'email_status':'prepared-not-sent'})
 prev['updated']=day
 STATE.write_text(json.dumps(prev,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--demo-test',action='store_true')
 parser.add_argument('--force',action='store_true',help='Run manual dry testing out of weekday schedule')
 args=parser.parse_args()
 now=dt.datetime.now(ZoneInfo('Europe/Madrid'))
 day=now.date().isoformat()
 if args.demo_test:
  cfg=settings()
  assert banned_candidate({'name':'Servicios de TDconsulting Málaga'},cfg)
  assert banned_candidate({'name':'Empresa Z','email':'administracion@topdigital.es'},cfg)
  assert not banned_candidate({'name':'Fontanería Centro','email':'contacto@centro.es'},cfg)
  prev=prior_history()
  assert known({'domain':'bonelaintegra.com'},prev)
  c={'name':'EJEMPLO LOCAL - NO PUBLICAR','craft':'plumber','activity':'Fontanería','services':['Fontanería'],
   'city':'Málaga','email':'prueba@example.net','phone':'+34950000000',
   'color':'#216F86','group':'web-mejorable',
   'about':'Fontanería en Málaga; exclusivamente una muestra local para verificar código.'}
  pages=make_pages(c,'Málaga','prueba', '')
  verify_static(pages,c)
  subject,body,_=create_mail(c,'https://example.net/propuesta/')
  assert '490 € + IVA' in body and subject=='Propuesta visual para la web'
  print('TEST OK: exclusiones, repetidos, estructura multipágina y email sin enviar')
  return
 if now.weekday()>=5 and not args.force:
  print('Fin de semana: sin actividad ni emails')
  return
 REPORT.mkdir(parents=True,exist_ok=True)
 OUT.mkdir(exist_ok=True)
 prev=prior_history(); cfg=settings()
 today_index=now.date().toordinal()%len(TOWN)
 town=TOWN[today_index]
 candidates,notes=osm(town)
 items=[];lookup=set()
 for row in candidates:
  c=candidate(row,town[0],cfg,prev)
  if not c:continue
  uniq=c.get('domain') or c['osm_id']
  if uniq in lookup:continue
  lookup.add(uniq);items.append(c)
 available_old=[x for x in items if x['website']]
 available_no=[x for x in items if not x['website']]
 made=[];counters={'sin-web-localizada':0,'web-mejorable':0}
 MAX_SCANNED=65;scanned=0
 # Seek 2 + 3, backfill from the other category if the source lacks candidates.
 for group,collection,desired,round_limit in [
   ('sin-web-localizada',available_no,2,14),
   ('web-mejorable',available_old,3,30),
   ('web-mejorable',available_old,5,20),
   ('sin-web-localizada',available_no,5,12)]:
  examined_this_round=0
  for c in collection:
   if len(made)>=5 or scanned>=MAX_SCANNED or examined_this_round>=round_limit:break
   if counters[group]>=desired:break
   if any(v['osm_id']==c['osm_id'] for v in made):continue
   scanned+=1
   examined_this_round+=1
   try:
    if group=='web-mejorable':
     selected=extract(c,cfg)
    else:
     ok,reason=checked_no_website(c)
     selected=info_without_website(c) if ok else None
     if selected:selected['site_evidence']=reason
    if not selected or banned_candidate(selected,cfg) or known(selected,prev):continue
    if not selected.get('phone') and not selected.get('email'):continue
    key=selected['domain'] or selected['osm_id']
    slug=slugify(selected['name'])+'-'+hashlib.sha256(key.encode()).hexdigest()[:6]
    pages=make_pages(selected,town[0],slug,'')
    verify_static(pages,selected)
    folder=OUT/slug
    # Idempotent: don't overwrite an existing proposal for the same business.
    if folder.exists():continue
    folder.mkdir(parents=True,exist_ok=True)
    for filename,content in pages.items():
     (folder/filename).write_text(content,encoding='utf-8')
    url=SITE_BASE+slug+'/'
    subj,body,compose=create_mail(selected,url)
    (folder/'propuesta-email.txt').write_text('Para: '+(selected.get('email') or 'sin email público')+
     '\nAsunto: '+subj+'\n\n'+body,encoding='utf-8')
    selected={**selected,'folder':slug,'demo_url':url,'compose_url':compose}
    made.append(selected);counters[group]+=1
    time.sleep(.4)
   except Exception as e:
    notes.append('Candidato omitido por fallo de verificación '+type(e).__name__)
  if len(made)>=5 or scanned>=MAX_SCANNED:break
 save_state(prev,made,day)
 report=make_report(day,town[0],made,notes,scanned)
 (REPORT/(day+'.md')).write_text(report,encoding='utf-8')
 (ROOT/'automation'/'issue-body.md').write_text(report,encoding='utf-8')
 write_manifest(day,made,notes,town[0])
 print('GENERADAS',len(made),'SIN_WEB',counters['sin-web-localizada'],
       'WEB_MEJORABLE',counters['web-mejorable'],'REVISIONES',scanned,'LOCALIDAD',town[0])
if __name__=='__main__':
 main()
