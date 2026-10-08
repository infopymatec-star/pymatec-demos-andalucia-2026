#!/usr/bin/env python3
"""Prueba única de la canalización Pymatec: empresa real verificada, demo y email preparado.

La búsqueda inicial de Bonela Integra se hizo sobre su web pública y sus datos
fueron confirmados previamente. El script vuelve a comprobarlos cuando puede.
No envía emails; la única prueba de envío la hace el usuario mediante Gmail.
"""
from datetime import date
from site_pages import make_pages
from pathlib import Path
import json
from free_daily import (
    ROOT, DEST, REPORTS, STATE, CRAFTS, extract_business, make_demo, create_note,
)

source = {
    'name': 'Bonela Integra S.L.',
    'website': 'https://www.bonelaintegra.com/',
    'domain': 'bonelaintegra.com',
    'craft': 'hvac',
    'osm_id': 'busqueda-web-publica-primera-empresa',
}
# Datos publicados en la web oficial y comprobados en la fase de selección.
verified = {
    **source,
    'email': 'estudio@bonelaintegra.com',
    'phone': '+34952028755',
    'logo': 'https://www.bonelaintegra.com/wp-content/uploads/2016/03/logobonelaintegratransparente.png.webp',
    'color': CRAFTS['hvac'][1],  # Paleta de propuesta; no se afirma que sea Pantone corporativo.
    'verified_url': source['website'],
    'services': ['Climatización', 'Fontanería', 'Agua caliente sanitaria', 'Protección contra incendios', 'Sistemas de gas', 'Ventilación'],
    'address': 'C. Miguel Berrocal, 14, 29580 Estación de Cártama, Málaga',
    'hours': 'Lunes a viernes · 09:00–14:00 y 16:00–19:00',
    'about': 'Bonela Integra S.L. cuenta con más de 25 años de experiencia en el sector de las instalaciones y servicios de mantenimiento. Es especialista en climatización, fontanería, agua caliente sanitaria, contraincendios, gas y ventilación. Su objetivo es encontrar soluciones adaptadas a las necesidades de cada proyecto.',
}
verification = 'Comprobación original de la búsqueda, sin petición adicional'
try:
    live = extract_business(source)
    if live and live.get('email','').lower() == verified['email']:
        verified.update(live)
        if not live.get('about'):
            verified['about'] = 'Bonela Integra S.L. cuenta con más de 25 años de experiencia en el sector de las instalaciones y servicios de mantenimiento. Es especialista en climatización, fontanería, agua caliente sanitaria, contraincendios, gas y ventilación.'
        verified['logo'] = live.get('logo') or verified['logo']
        verification = 'Web oficial y email contrastados de nuevo durante la ejecución'
    else:
        verification = 'Web original contrastada al seleccionar la empresa; sin revalidación completa en runner'
except Exception as e:
    verification = 'Web original contrastada al seleccionar la empresa; no se pudo repetir petición: ' + type(e).__name__

verified['about'] = ('Bonela Integra S.L. cuenta con más de 25 años de experiencia '
    'en instalaciones y servicios de mantenimiento. Se dedica a climatización, '
    'fontanería, agua caliente sanitaria, protección contra incendios, sistemas '
    'de gas y ventilación. Su web destaca el trabajo en equipo y la búsqueda '
    'de soluciones adaptadas a cada proyecto.')
# Información específica confirmada en las páginas oficiales de Bonela.
verified.update({
    'hero_title': 'Instalaciones que hacen funcionar cada espacio.',
    'hero_subtitle': 'Climatización, fontanería y mantenimiento industrial con más de 25 años de experiencia.',
    'services_intro': 'Instalaciones técnicas para edificios, espacios profesionales y proyectos industriales.',
    'about_home_title': 'Más de 25 años aportando soluciones.',
    'about_title': 'Más de 25 años comprometidos con las instalaciones.',
    'about_more': 'Nuestra actividad abarca desde el diseño y la ejecución de instalaciones hasta los servicios de mantenimiento. Apostamos por el trabajo en equipo y por encontrar la solución más adecuada para cada proyecto.',
    'footer_description': 'Instalaciones y mantenimiento industrial: climatización, fontanería, protección contra incendios, agua caliente sanitaria, gas y ventilación.',
    'experience': '+25 años',
    'hero_image': 'https://www.bonelaintegra.com/wp-content/uploads/2023/03/instalaciones-edar-estepona.jpg.webp',
    'secondary_image': 'https://www.bonelaintegra.com/wp-content/uploads/2023/03/Hotel-Angela.jpg.webp',
    'projects': [
      {'title': 'Hospital Comarcal de la Axarquía', 'description': 'Fontanería y climatización', 'image': 'https://www.bonelaintegra.com/wp-content/uploads/2023/03/03hospitalvelez_alb-300x220.jpg.webp'},
      {'title': 'Estación Marítima', 'description': 'Climatización, fontanería, saneamiento y protección contra incendios', 'image': 'https://www.bonelaintegra.com/wp-content/uploads/2023/03/10estmaritima_alb-300x200.jpg.webp'},
      {'title': 'Sede BestSeller', 'description': 'Energía solar, fontanería, saneamiento y riego', 'image': 'https://www.bonelaintegra.com/wp-content/uploads/2023/03/bESTSELLER-300x225.jpg.webp'},
    ],
})
city = 'Estación de Cártama, Málaga'
day = date.today().isoformat()
slug, webpage = make_demo(verified, city)
pages = make_pages(verified, city, slug, webpage)
folder = DEST / slug
folder.mkdir(parents=True, exist_ok=True)
for filename, source_html in pages.items():
    (folder / filename).write_text(source_html, encoding='utf-8')
url = 'https://infopymatec-star.github.io/pymatec-demos-andalucia-2026/auto-demos/' + slug + '/'
email, compose = create_note({'email':verified['email'],'demo_url':url}, day)
assert email.count(url) == 1
assert 'Asunto: Propuesta visual para la web' in email
assert 'Presupuesto cerrado: 490 € + IVA.' in email
assert verified['logo'] in webpage
assert 'noindex' in webpage
assert 'id="sobre-nosotros"' not in pages['index.html']
assert 'id="contacto"' not in pages['index.html']
assert 'id="sobre-nosotros"' in pages['sobre-nosotros.html']
assert 'class="sample-form"' in pages['contacto.html']
assert 'Web oficial' not in pages['contacto.html']
assert 'Visitar sitio original' not in pages['contacto.html']
assert 'C. Miguel Berrocal' in pages['contacto.html']
assert 'instalaciones que hacen funcionar' in pages['index.html'].lower()
assert 'Algunos de nuestros trabajos' in pages['index.html']
assert '03hospitalvelez_alb' in pages['index.html']
for content_page in pages.values():
    assert 'Teléfono' in content_page and 'estudio@bonelaintegra.com' in content_page
    assert 'C. Miguel Berrocal' in content_page
    assert 'Una web clara' not in content_page
    assert 'Visitar sitio original' not in content_page
assert 'Formular' in pages['contacto.html']

assert 'Más de 25' in pages['sobre-nosotros.html'] or 'más de 25' in pages['sobre-nosotros.html']
(folder / 'propuesta-email.txt').write_text(email, encoding='utf-8')
REPORTS.mkdir(parents=True, exist_ok=True)
report = f"""# Prueba única de Pymatec: primera empresa encontrada

- Empresa: {verified['name']}
- Web oficial: {verified['website']}
- Email comercial público (NO es destinatario de la prueba): {verified['email']}
- Demo publicada (tras GitHub Pages): {url}
- Logotipo tomado del sitio oficial: {verified['logo']}
- Color: propuesta de paleta basada en sector o tema de la web (no necesariamente color oficial).
- Fuente: búsqueda de empresas con web pública en Málaga y comprobación en su sitio.
- Estado de datos: {verification}
- Email tipo: `{folder.relative_to(ROOT)}/propuesta-email.txt`
- Asunto: Propuesta visual para la web
- **No se envía ningún mensaje a la empresa.** El correo de prueba se enviará exclusivamente a joselss86@hotmail.com mediante la cuenta de Pymatec.
- Esta maqueta es no oficial y su material es ilustrativo.
"""
(REPORTS / ('prueba-'+day+'-bonela-integra.md')).write_text(report, encoding='utf-8')
# La carpeta se publica desde GitHub Pages; el reporte y correo se conservan.
index = DEST / 'index.html'
entry = f'<li><a href="{slug}/">Bonela Integra S.L. — prueba</a></li>'
if index.exists():
    old = index.read_text(encoding='utf-8')
    if f'href="{slug}/"' not in old:
        if '</ul>' in old: old = old.replace('</ul>', entry+'</ul>',1)
        else: old = old.replace('</body>',entry+'</body>',1)
        index.write_text(old,encoding='utf-8')
print('PRUEBA_OK',json.dumps({'empresa':verified['name'],'demo':url,'origen':verification,'email_prueba':'joselss86@hotmail.com'},ensure_ascii=False))
