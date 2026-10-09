#!/usr/bin/env python3
"""Rebuild existing four Pymatec concepts with the approved 3-page template.
No prospecting, no emails, no claims of verification or authorization.
"""
from pathlib import Path
from site_pages import make_pages
from prospecting_weekdays import verify_static

ROOT=Path(__file__).resolve().parents[1]
COMPANIES=[
 dict(slug="servicios-integrales-cartama",name="Servicios Integrales Cártama",city="Cártama",craft="plumber",activity="Piscinas e instalaciones",email="piscinascartama@hotmail.com",color="#1674a5",logo="https://piscinasmlg.com/wp-content/uploads/2020/03/logo-sin-fraseServicios-Integrales-Cartama-600x222.png",hero_image="https://piscinasmlg.com/wp-content/uploads/2020/10/piscinadeaceroblancokit500eco-14288-600x600.jpg",services=["Piscinas desmontables","Mantenimiento de piscinas","Instalaciones y reformas"],website="https://piscinasmlg.com/"),
 dict(slug="imperespuma-malaga",name="Imperespuma Málaga",city="Málaga",craft="roofer",activity="Impermeabilización",email="info@imperespuma.es",color="#253f56",logo="https://imperespumamalaga.com/wp-content/uploads/2025/10/dark-logo.png",hero_image="https://imperespumamalaga.com/wp-content/uploads/elementor/thumbs/Roofing-rd8jgrzn2kskgs5q78zh3c72rlkcomb5qw45n8ln5c.webp",services=["Impermeabilización con tela asfáltica","Aislamiento con poliuretano","Protección contra el fuego"],website="https://imperespumamalaga.com/"),
 dict(slug="reformas-francisco-paz",name="Reformas Francisco Paz",city="Málaga",craft="handyman",activity="Reformas",email="info@reformasfranciscopaz.es",color="#d29a28",logo="https://www.reformasfranciscopaz.es/images/reformasFranciscoPaz.png",hero_image="https://www.reformasfranciscopaz.es/images/slides/img0.jpg",services=["Reformas integrales","Reformas de baños y cocinas","Reformas de locales"],website="https://www.reformasfranciscopaz.es/"),
 dict(slug="fahala-garden",name="Fahala Garden",city="Cártama",craft="gardener",activity="Jardinería",email="fahalagarden@gmail.com",color="#3c8642",logo="https://fahalagarden.com/wp-content/uploads/2022/11/fahala-garden-logo-png.png",hero_image="https://fahalagarden.com/wp-content/uploads/2022/11/empresa-jardineria-en-malaga.jpg",services=["Mantenimiento de jardines","Sistemas de riego","Diseño de jardines y paisajismo","Mantenimiento de piscinas"],website="https://fahalagarden.com/"),
]
def main():
 for c in COMPANIES:
  # No testimonials, projects, accreditations, years, staff or claimed services without evidence.
  data={**c,
   "hero_title":c["activity"]+" en "+c["city"]+".",
   "secondary_image":c["hero_image"],
   "hero_subtitle":"Consulta los servicios disponibles y solicita información sobre tu proyecto.",
   "about":c["name"]+" ofrece servicios relacionados con "+c["activity"].lower()+". Consulta las especialidades y solicita información sobre el servicio que necesitas.",
   "about_title":c["activity"]+" y atención al cliente",
   "about_more":"Ponte en contacto con la empresa para confirmar servicios, disponibilidad y condiciones.",
   "services_intro":"Descubre las principales áreas de actividad publicadas por la empresa.",
   "footer_description":c["activity"]+" · "+c["city"]+". Consulta los detalles con la empresa.",
   "trust_1":"Información de servicios",
   "trust_2":"Contacto directo",
   "trust_3":"Presentación clara",
   "trust_4":"Solicitar información",
   "projects":[],
   "logo":c["logo"],
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
