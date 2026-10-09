#!/usr/bin/env python3
"""Rebuild existing four Pymatec concepts with the approved 3-page template.
No prospecting, no emails, no claims of verification or authorization.
"""
from pathlib import Path
from site_pages import make_pages
from prospecting_weekdays import verify_static

ROOT=Path(__file__).resolve().parents[1]
COMPANIES=[
 dict(slug="servicios-integrales-cartama",name="Servicios Integrales Cártama",city="Cártama",craft="plumber",activity="Piscinas e instalaciones",email="piscinascartama@hotmail.com",color="#176b89",services=["Piscinas e instalaciones"],website="https://piscinasmlg.com/"),
 dict(slug="imperespuma-malaga",name="Imperespuma Málaga",city="Málaga",craft="roofer",activity="Impermeabilización",email="info@imperespuma.es",color="#2d687d",services=["Impermeabilización"],website="https://imperespumamalaga.com/"),
 dict(slug="reformas-francisco-paz",name="Reformas Francisco Paz",city="Málaga",craft="handyman",activity="Reformas",email="info@reformasfranciscopaz.es",color="#986647",services=["Reformas"],website="https://www.reformasfranciscopaz.es/"),
 dict(slug="fahala-garden",name="Fahala Garden",city="Cártama",craft="gardener",activity="Jardinería",email="fahalagarden@gmail.com",color="#39754c",services=["Jardinería"],website="https://fahalagarden.com/"),
]
def main():
 for c in COMPANIES:
  # No testimonials, projects, accreditations, years, staff or claimed services without evidence.
  data={**c,
   "hero_title":c["activity"]+" en "+c["city"]+".",
   "hero_subtitle":"Consulta los servicios disponibles y solicita información sobre tu proyecto.",
   "about":c["name"]+" figura públicamente asociado a la actividad de "+c["activity"].lower()+". Esta presentación es un concepto visual; los textos definitivos serán confirmados por la empresa.",
   "about_title":c["activity"]+" y atención al cliente",
   "about_more":"Ponte en contacto con la empresa para confirmar servicios, disponibilidad y condiciones.",
   "services_intro":"Presentación inicial de la actividad. El detalle de servicios se completará con información validada por la empresa.",
   "footer_description":c["activity"]+" · "+c["city"]+". Consulta los detalles con la empresa.",
   "trust_1":"Información de servicios",
   "trust_2":"Contacto directo",
   "trust_3":"Presentación clara",
   "trust_4":"Solicitar información",
   "projects":[],
   "logo":None,
   "phone":"",
   "address":"",
   "hours":"",
  }
  pages=make_pages(data,c["city"],c["slug"],"")
  verify_static(pages,data)
  folder=ROOT/"auto-demos"/c["slug"]
  folder.mkdir(parents=True,exist_ok=True)
  for filename,content in pages.items():
   (folder/filename).write_text(content,encoding="utf-8")
  print("TEMPLATE_OK",c["name"],len(pages),"pages")
if __name__=="__main__":main()
