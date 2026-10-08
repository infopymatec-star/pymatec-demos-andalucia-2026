"""Plantillas multipágina Pymatec: contenido de negocio y contacto verificables.
Las demos públicas son conceptuales, con formulario desactivado y sin links
al sitio original. Las fotos de trabajos solo se muestran cuando hay evidencia.
"""
from html import escape
from urllib.parse import quote


def E(value):
    return escape(str(value or ''), quote=True)


SERVICES = {
 'climatización': 'Climatización y sistemas de aire acondicionado para edificios y espacios profesionales.',
 'fontanería': 'Redes de suministro, instalaciones de fontanería y sistemas de saneamiento.',
 'agua caliente sanitaria': 'Instalaciones y equipos para la producción de agua caliente sanitaria.',
 'protección contra incendios': 'Sistemas de detección y extinción de incendios, instalación y mantenimiento.',
 'contraincendios': 'Sistemas de detección y extinción de incendios, instalación y mantenimiento.',
 'sistemas de gas': 'Instalaciones de gas, mantenimiento y soluciones adaptadas a cada proyecto.',
 'ventilación': 'Sistemas de ventilación y renovación de aire para diferentes edificios.',
 'energía solar': 'Instalaciones solares y soluciones de aprovechamiento energético.',
 'electricidad': 'Instalaciones eléctricas y trabajos de mantenimiento.',
 'carpintería': 'Fabricación, instalación y acabados en madera.',
}

PHOTOS = {
 'hvac': 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1600&q=85',
 'electrician': 'https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=1600&q=85',
 'carpenter': 'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1600&q=85',
 'plumber': 'https://images.unsplash.com/photo-1585704032915-c3400ca199e7?auto=format&fit=crop&w=1600&q=85',
 'gardener': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=1600&q=85',
}
FALLBACK = 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1600&q=85'
OTHER_PHOTO = 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=1200&q=82'

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--brand:#276b78;--brand-dark:#184a56;--ink:#1d3138;--muted:#61727a;--soft:#f4f7f6;--cream:#f8f7f2;--line:#dce5e5;--accent:#d9a672}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#fff;font:16px/1.7 'DM Sans',system-ui,sans-serif}
a{color:inherit;text-decoration:none}button,input,textarea{font:inherit}.wrap{width:min(1200px,90%);margin:auto}
.demo-note{background:#f0f4f4;color:#52676d;text-align:center;font-size:11px;letter-spacing:.04em;padding:7px 12px}
.site-header{background:#fff;border-bottom:1px solid #edf0ee;position:sticky;top:0;z-index:30;box-shadow:0 2px 16px #1b343a08}
.navigation{display:flex;align-items:center;justify-content:space-between;gap:28px;min-height:91px}
.brand{display:flex;align-items:center;gap:12px;min-width:0}.brand img{height:58px;max-width:160px;object-fit:contain}.brand span{font-family:Manrope,sans-serif;font-size:16px;font-weight:800;line-height:1.16;letter-spacing:-.04em;max-width:160px}
.menu{display:flex;align-items:center;gap:27px}.menu a{font-size:13px;font-weight:800;color:#51636b;white-space:nowrap}
.menu a.active,.menu a:hover{color:var(--brand)}
.btn{border:0;border-radius:999px;background:var(--brand);color:#fff;padding:15px 22px;display:inline-flex;align-items:center;justify-content:center;gap:12px;cursor:pointer;font-weight:800;font-size:13px;white-space:nowrap;transition:transform .18s,background .18s}
.btn:hover{background:var(--brand-dark);transform:translateY(-2px)}.btn.light{background:#fff;color:var(--brand-dark)}.btn.light:hover{background:#e8f0f1}
.eyebrow{font-size:11px;letter-spacing:.19em;text-transform:uppercase;font-weight:800;color:var(--brand)}
h1,h2,h3{font-family:Manrope,'DM Sans',sans-serif;line-height:1.12;letter-spacing:-.05em}
h1{font-size:clamp(43px,5.4vw,75px);margin:21px 0}h2{font-size:clamp(32px,4vw,53px);margin:18px 0}h3{font-size:21px;margin:12px 0}
p{margin:0 0 17px;color:var(--muted)}.lead{font-size:18px;line-height:1.82}
.section{padding:95px 0}.section-intro{max-width:720px;margin-bottom:37px}
.section-intro p{font-size:17px}.hero{padding:65px 0 70px;background:var(--cream);position:relative;overflow:hidden}
.hero-layout{display:grid;grid-template-columns:1fr 1.02fr;gap:48px;align-items:center}
.hero h1{max-width:650px}.hero p{max-width:600px;font-size:18px}
.hero-photo{min-height:550px;border-radius:8px 105px 8px 80px;background-size:cover;background-position:center;position:relative;box-shadow:0 30px 70px #152e3530}
.hero-photo:after{content:'';position:absolute;inset:0;border-radius:inherit;background:linear-gradient(180deg,transparent 50%,#1730384a)}
.hero-floating{position:absolute;z-index:2;left:-25px;bottom:34px;background:#fff;box-shadow:0 16px 50px #19363c35;padding:18px 23px;border-radius:17px;max-width:260px}
.hero-floating strong{display:block;font:800 28px Manrope,sans-serif;color:var(--brand);letter-spacing:-.06em;line-height:1.1}
.hero-floating span{display:block;font-size:13px;color:#576a70;margin-top:4px}
.hero-sub{display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-top:26px}.hero-sub a:not(.btn){font-size:13px;font-weight:800;color:var(--brand)}
.service-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:21px}
.svc{background:#fff;border:1px solid var(--line);border-radius:21px;overflow:hidden;transition:transform .18s,box-shadow .18s}
.svc:hover{transform:translateY(-4px);box-shadow:0 18px 50px #1a384211}
.svc-media{height:172px;background-size:cover;background-position:center;position:relative}
.svc-number{position:absolute;top:15px;left:15px;background:#fff;border-radius:99px;font-size:12px;font-weight:800;color:var(--brand);padding:6px 10px}
.svc-body{padding:25px 26px 27px}.svc h3{font-size:20px;margin:0 0 9px}.svc p{font-size:14px;margin:0}
.soft{background:var(--soft)}
.intro-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:68px;align-items:center}
.intro-photo{min-height:450px;border-radius:80px 8px 75px 8px;background-size:cover;background-position:center}
.intro-side p{font-size:18px}.fact-row{display:grid;grid-template-columns:repeat(2,1fr);gap:13px;margin:27px 0}
.fact{padding:18px 21px;background:#f1f7f5;border-radius:15px;font-weight:700;color:#36505a;font-size:14px}
.project-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.project{overflow:hidden;border-radius:20px;border:1px solid var(--line);background:#fff}
.project-photo{height:235px;width:100%;display:block;object-fit:cover}
.project-copy{padding:20px 23px}.project h3{font-size:18px;margin:0 0 7px}.project p{font-size:13px;margin:0}
.cta{background:linear-gradient(105deg,#18444d,#266875);color:#fff;padding:64px 0}
.cta-layout{display:flex;align-items:center;justify-content:space-between;gap:35px}
.cta h2{color:#fff;max-width:700px;margin:10px 0;font-size:clamp(30px,3.3vw,47px)}
.cta p{color:#d9e8e9;margin:0}.cta .eyebrow{color:#d8e8e5}
.pagehero{background:var(--cream);min-height:325px;display:grid;align-items:center;position:relative;overflow:hidden}
.pagehero:before{content:'';position:absolute;right:-60px;top:-135px;width:430px;height:430px;background:#e4edeb;border-radius:50%}
.pagehero .wrap{position:relative;padding:70px 0}.pagehero h1{font-size:clamp(42px,5vw,67px);margin:13px 0}.pagehero p{font-size:18px;max-width:710px}
.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:68px;align-items:center}
.about-photo{width:100%;height:500px;object-fit:cover;border-radius:80px 8px 75px 8px}
.about-copy .lead{font-size:18px}.tag-list{display:flex;gap:11px;flex-wrap:wrap;margin-top:20px}
.tag{padding:10px 16px;border:1px solid #cddfdf;border-radius:99px;color:#335963;font-size:13px;font-weight:800;background:#f6fbfa}
.contact-grid{display:grid;grid-template-columns:.85fr 1.15fr;gap:45px;align-items:start}
.contact-panel{padding:34px;background:var(--soft);border-radius:24px}
.contact-line{padding:18px 0;border-bottom:1px solid #dce5e5}.contact-line:last-child{border-bottom:0}
.contact-line small{display:block;color:var(--brand);font-size:11px;text-transform:uppercase;letter-spacing:.14em;font-weight:800;margin-bottom:5px}
.contact-line a,.contact-line span{overflow-wrap:anywhere;font-weight:750;font-size:17px;color:#243941}
.form-panel{border:1px solid var(--line);padding:36px;border-radius:25px;box-shadow:0 22px 50px #2136400c}
.form-panel h2{font-size:31px;margin:0 0 9px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.form-panel label{font-weight:750;color:#344951;font-size:13px;display:block;margin-top:17px}
.form-panel input,.form-panel textarea{background:#fafcfc;border:1px solid #d9e3e5;display:block;border-radius:13px;padding:13px 14px;width:100%;margin-top:7px;color:#213942}
.form-panel textarea{min-height:133px;resize:vertical}.form-info{background:#f0f6f6;border-radius:13px;padding:13px 16px;font-size:12px;margin:18px 0;color:#48636a}
.demo-form-button{opacity:.75;cursor:not-allowed}
.site-footer{background:#192f36;color:#eef5f3;padding:70px 0 0}
.footer-grid{display:grid;grid-template-columns:1.25fr .8fr 1.05fr;gap:65px;padding-bottom:62px}
.footer-brand{font-size:21px;font-weight:800;letter-spacing:-.04em;color:#fff}
.site-footer h3{font-size:14px;text-transform:uppercase;letter-spacing:.09em;font-weight:800;margin:0 0 19px;color:#e1eee9}
.site-footer p{color:#bacbc9;font-size:13px;line-height:1.9;margin-top:14px;max-width:320px}
.footer-links a{display:block;color:#d3e2df;margin:0 0 12px;font-size:14px}
.footer-contact a,.footer-contact span{display:block;color:#d3e2df;font-size:14px;margin-bottom:13px;overflow-wrap:anywhere}
.footer-contact strong{color:#fff;font-size:12px;display:block;letter-spacing:.05em}
.footer-bottom{border-top:1px solid #385057;padding:15px 0;color:#b0c2c0;font-size:11px;display:flex;justify-content:space-between;gap:25px}
@media(max-width:1020px){.hero-layout,.intro-grid,.about-grid{gap:28px}.hero-photo{min-height:440px}.menu{gap:17px}.navigation{gap:14px}}
@media(max-width:800px){.navigation{flex-wrap:wrap;padding:11px 0}.menu{order:3;width:100%;justify-content:center;padding:4px 0 8px}.hero-layout,.intro-grid,.about-grid,.contact-grid{grid-template-columns:1fr}.hero-layout{gap:36px}.hero-photo{min-height:460px}.hero-floating{left:15px}.section{padding:70px 0}.service-grid,.project-grid{grid-template-columns:repeat(2,1fr)}.footer-grid{gap:25px}.cta-layout{align-items:flex-start}}
@media(max-width:560px){.wrap{width:min(100% - 38px,1200px)}.navigation{gap:8px}.brand img{height:44px;max-width:140px}.brand span{font-size:13px;max-width:115px}.navigation>.btn{padding:12px 14px;font-size:11px}.menu{justify-content:space-between}.menu a{font-size:12px}.hero{padding:50px 0}.hero h1{font-size:42px}.hero-photo{min-height:350px;border-radius:8px 70px 8px 60px}.hero-floating{left:14px;bottom:15px}.service-grid,.project-grid,.footer-grid,.form-grid{grid-template-columns:1fr}.cta-layout{display:block}.cta .btn{margin-top:20px}.intro-photo,.about-photo{height:300px;min-height:300px}.footer-grid{gap:32px}.footer-bottom{display:block}.form-panel,.contact-panel{padding:24px}}
"""


MODERN_CSS = """
/* Editorial treatment: large meaningful imagery, legible navigation and discreet motion. */
:root{--ink:#15323a;--muted:#5f7075;--soft:#f4f8f7;--cream:#f8f7f2}
body{font-size:16px}
.site-header{box-shadow:0 8px 28px #142f3409}
.navigation{min-height:88px;gap:20px}
.menu{gap:20px}
.menu a{font-size:12px;letter-spacing:.01em}
.menu a.active{position:relative}
.menu a.active::after{content:'';position:absolute;bottom:-15px;left:0;right:0;background:var(--brand);height:2px}
.demo-note{font-size:10px;padding:6px 12px;letter-spacing:.065em}
.hero{background:linear-gradient(120deg,#f4f8f7 0%,#fbf8f1 90%);padding:76px 0 86px}
.hero-layout{grid-template-columns:1.06fr 1fr;gap:65px}
.hero h1{font-size:clamp(44px,5.2vw,74px);line-height:1.075;letter-spacing:-.065em}
.hero .lead{line-height:1.76}
.hero-photo{min-height:580px;border-radius:7px 110px 8px 85px;box-shadow:0 30px 70px #11364029}
.hero-photo:before{content:'';position:absolute;inset:0;border-radius:inherit;background:linear-gradient(120deg,transparent 40%,#092a3722)}
.hero-floating{background:rgba(255,255,255,.95);backdrop-filter:blur(9px);padding:18px 25px;max-width:270px}
.trust-strip{background:#193c45;color:#f4fbfb;border-bottom:1px solid #2e5860}
.trust-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;padding:23px 0}
.trust-item{display:flex;align-items:center;gap:13px;font-size:13px;font-weight:760;line-height:1.4}
.trust-icon{color:#b2d6d7;font-size:19px;font-weight:800}
.section{padding:94px 0}
.section-intro{max-width:795px}
.section-intro p{font-size:18px}
.svc{border-radius:8px 28px 8px 28px}
.svc-media{height:202px}
.svc-body{min-height:172px;display:flex;flex-direction:column;justify-content:flex-start}
.svc h3{font-size:21px}
.project{border-radius:7px 26px 7px 26px}
.project-photo{height:260px;background:#e9eeee}
.project-copy{padding:22px 24px 25px}
.project-copy p{font-size:14px;line-height:1.65}
.project-grid .project:first-child{grid-column:span 1}
.photo-note{font-size:12px;color:#7a8b91;margin-top:15px}
.project-kicker{font-size:11px;color:var(--brand);font-weight:800;letter-spacing:.13em;text-transform:uppercase;display:block;margin-bottom:7px}
.intro-photo{min-height:470px}
.intro-side .lead{font-size:18px}
.intro-side p{line-height:1.8}
.btn{min-height:48px}
.btn:focus-visible,.menu a:focus-visible{outline:3px solid #8ebfc6;outline-offset:3px}
.footer-bottom{font-size:10px}
.mobile-quickbar{display:none}
@media(max-width:1050px){.menu{gap:12px}.hero-layout{gap:35px}.hero h1{font-size:clamp(42px,5.2vw,65px)}.brand img{max-width:125px}}
@media(max-width:810px){.trust-grid{grid-template-columns:repeat(2,1fr)}.hero-layout{grid-template-columns:1fr}.hero-photo{min-height:490px}.menu{justify-content:space-between;overflow-x:auto;scrollbar-width:none}.menu::-webkit-scrollbar{display:none}.menu a.active::after{bottom:-3px}.site-header{position:relative}}
@media(max-width:580px){body{padding-bottom:72px}.hero{padding:43px 0 60px}.hero h1{font-size:clamp(39px,10.8vw,52px)}.hero .lead{font-size:16px}.hero-photo{min-height:360px}.trust-grid{grid-template-columns:repeat(2,1fr);gap:12px 18px;padding:19px 0}.trust-item{font-size:11px}.trust-icon{font-size:15px}.svc-body{min-height:unset}.section-intro p{font-size:16px}.service-grid{grid-template-columns:1fr}.project-photo{height:235px}.mobile-quickbar{position:fixed;bottom:0;left:0;right:0;z-index:40;background:rgba(255,255,255,.98);box-shadow:0 -9px 25px #152d3416;padding:10px 18px calc(10px + env(safe-area-inset-bottom));display:flex;gap:10px}.mobile-quickbar a{flex:1;border-radius:12px;min-height:46px;display:grid;place-items:center;font-weight:800;font-size:13px;background:#eaf4f3;color:#244b54}.mobile-quickbar a:last-child{background:var(--brand);color:#fff}.site-footer{padding-top:58px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important}}
"""

def make_pages(info, city, slug, document):
    """Three static, linked customer-facing pages. Form remains a disabled visual example."""
    name=E(info.get('name'))
    short=E(info.get('name','').rstrip('.'))
    city=E(city)
    activity=E(info.get('activity') or 'Instalaciones y servicios')
    brand=E(info.get('color') or '#276b78')
    photo=E(info.get('hero_image') or PHOTOS.get(info.get('craft'),FALLBACK))
    secondary=E(info.get('secondary_image') or OTHER_PHOTO)
    logo=info.get('logo') or ''
    logo_html=(f'<img src="{E(logo)}" alt="Logotipo de {name}" loading="eager">' if logo else '')
    email=E(info.get('email'))
    phone_raw=info.get('phone') or ''
    phone=E(phone_raw)
    tel=E(''.join(c for c in phone_raw if c.isdigit() or c=='+'))
    address=E(info.get('address'))
    hours=E(info.get('hours'))
    about=E(info.get('about') or ('Conoce los servicios y especialidades de '+info.get('name','la empresa')+'. Estamos a tu disposición para ampliar información sobre nuestros trabajos.'))
    services=info.get('services') or [info.get('activity') or 'Servicios profesionales']
    services=[str(s)[:90] for s in services][:9]
    has_experience=bool(info.get('experience'))
    experience=E(info.get('experience') or '')
    service_cards=[]
    service_tags=[]
    for i,service in enumerate(services):
        key=service.strip().lower()
        description=SERVICES.get(key, 'Consulta nuestros servicios y soluciones para tus necesidades.')
        image=(info.get('service_images') or [])
        image=image[i] if i<len(image) else [photo,secondary,OTHER_PHOTO][i%3]
        service_cards.append(
           f'<article class="svc"><div class="svc-media" style="background-image:url(&quot;{E(image)}&quot;)">'
           f'<span class="svc-number">{i+1:02d} / {len(services):02d}</span></div>'
           f'<div class="svc-body"><h3>{E(service)}</h3><p>{E(description)}</p></div></article>')
        service_tags.append(f'<span class="tag">{E(service)}</span>')
    project_cards=[]
    for p in (info.get('projects') or [])[:6]:
        if not p.get('title') or not p.get('image'): continue
        project_cards.append('<article class="project">'
         +f'<img class="project-photo" loading="lazy" src="{E(p["image"])}" alt="{E(p["title"])}">'
         +f'<div class="project-copy"><span class="project-kicker">Proyecto realizado</span><h3>{E(p["title"])}</h3><p>{E(p.get("description","Trabajos de instalaciones y mantenimiento"))}</p></div></article>')
    phone_html=f'<a href="tel:{tel}">{E(info.get("phone_display") or phone_raw)}</a>' if phone_raw else '<span>Consúltanos por correo</span>'
    address_html=f'<div class="contact-line"><small>Dirección</small><span>{address}</span></div>' if address else ''
    hours_html=f'<div class="contact-line"><small>Horario</small><span>{hours}</span></div>' if hours else ''
    css=CSS.replace('--brand:#276b78;',f'--brand:{brand};')
    css += MODERN_CSS
    def page(filename,title,body):
        nav=''.join(
          f'<a class="{"active" if url==filename else ""}" href="{url}">{label}</a>'
          for url,label in [
              ('index.html','Inicio'),
              ('index.html#servicios','Servicios'),
              ('index.html#proyectos','Proyectos'),
              ('sobre-nosotros.html','Sobre nosotros'),
              ('contacto.html','Contacto')
          ])
        header=f'''<div class="demo-note">Propuesta conceptual no oficial · Imágenes ilustrativas salvo fotografías de trabajos identificados</div>
        <header class="site-header"><div class="wrap navigation">
        <a class="brand" href="index.html">{logo_html}<span>{name}</span></a>
        <nav class="menu" aria-label="Principal">{nav}</nav>
        <a class="btn" href="contacto.html">Pedir presupuesto ↗</a></div></header>'''
        footer=f'''<footer class="site-footer"><div class="wrap footer-grid">
          <div><a class="footer-brand" href="index.html">{name}</a>
             <p>{E(info.get("footer_description") or "Servicios profesionales, instalación y mantenimiento. Información y presupuesto bajo consulta.")}</p>
          </div><div><h3>Enlaces</h3><div class="footer-links">
             <a href="index.html">Inicio</a><a href="index.html#servicios">Servicios</a>
             <a href="sobre-nosotros.html">Sobre nosotros</a><a href="contacto.html">Contáctanos</a></div></div>
          <div class="footer-contact"><h3>Contacto</h3>
             <strong>Teléfono</strong>{phone_html}<strong>Correo electrónico</strong>
             <a href="mailto:{email}">{email}</a>
             {f'<strong>Dirección</strong><span>{address}</span>' if address else ''}
             {f'<strong>Horario</strong><span>{hours}</span>' if hours else ''}</div></div>
          <div class="wrap footer-bottom"><span>© {name} · Presentación de muestra</span>
             <span>Demo no oficial por Pymatec · Formulario desactivado</span></div></footer>'''
        return ('<!doctype html><html lang="es"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           '<meta name="robots" content="noindex,nofollow,noarchive">'
           f'<meta name="description" content="Servicios e información de {name}">'
           f'<title>{E(title)} · {name}</title><style>{css}</style></head><body>'
           +header+'<main>'+body+'</main>'+footer
           +('<div class="mobile-quickbar"><a href="tel:'+tel+'">☎ Llamar</a><a href="contacto.html">Solicitar presupuesto ↗</a></div>' if phone_raw else
             '<div class="mobile-quickbar"><a href="sobre-nosotros.html">Sobre nosotros</a><a href="contacto.html">Contactar ↗</a></div>')
           +'</body></html>')
    # HOME: no sales pitch about the website.
    expnote=(f'<div class="hero-floating"><strong>{experience}</strong><span>de experiencia en el sector</span></div>' if has_experience else '')
    home=f'''<section class="hero"><div class="wrap hero-layout"><div>
        <span class="eyebrow">Instalaciones · Servicios profesionales · {city}</span>
        <h1>{E(info.get("hero_title") or "Soluciones profesionales para cada proyecto.")}</h1>
        <p class="lead">{E(info.get("hero_subtitle") or about[:180])}</p>
        <div class="hero-sub"><a class="btn" href="contacto.html">Solicitar presupuesto ↗</a>
        <a href="#servicios">Descubre nuestros servicios ↓</a></div></div>
        <div class="hero-photo" role="img" aria-label="Fotografía de un proyecto de instalaciones" style="background-image:url(&quot;{photo}&quot;)">{expnote}</div></div></section>
        <div class="trust-strip"><div class="wrap trust-grid">
        <div class="trust-item"><span class="trust-icon">✦</span><span>{E(info.get("trust_1") or "Experiencia en el sector")}</span></div>
        <div class="trust-item"><span class="trust-icon">⌁</span><span>{E(info.get("trust_2") or "Atención profesional")}</span></div>
        <div class="trust-item"><span class="trust-icon">↗</span><span>{E(info.get("trust_3") or "Servicios especializados")}</span></div>
        <div class="trust-item"><span class="trust-icon">◉</span><span>{E(info.get("trust_4") or "Solicita información")}</span></div>
        </div></div>
        <section class="section" id="servicios"><div class="wrap">
        <div class="section-intro"><span class="eyebrow">Qué hacemos</span><h2>Servicios e instalaciones</h2>
        <p>{E(info.get("services_intro") or "Conoce nuestras principales áreas de trabajo y encuentra la solución que necesitas.")}</p></div>
        <div class="service-grid">{''.join(service_cards)}</div></div></section>
        <section class="section soft"><div class="wrap intro-grid">
        <div class="intro-photo" role="img" aria-label="Fotografía ilustrativa de instalaciones" style="background-image:url(&quot;{secondary}&quot;)"></div>
        <div class="intro-side"><span class="eyebrow">Conoce nuestra empresa</span>
        <h2>{E(info.get("about_home_title") or "Experiencia y soluciones a medida.")}</h2>
        <p>{about}</p><a class="btn" href="sobre-nosotros.html">Sobre nosotros ↗</a></div></div></section>'''
    if project_cards:
        home+=f'''<section class="section" id="proyectos"><div class="wrap"><div class="section-intro">
          <span class="eyebrow">Proyectos realizados</span><h2>Trabajos que hablan por nosotros.</h2>
          <p>Instalaciones ejecutadas en edificios y espacios de diferentes características.</p></div>
          <div class="project-grid">{''.join(project_cards[:3])}</div>
          <p class="photo-note">Fotografías y referencias de trabajos publicados por la empresa.</p></div></section>'''
    home+='''<section class="cta"><div class="wrap cta-layout"><div>
      <span class="eyebrow">¿Hablamos?</span><h2>Cuéntanos qué necesitas para tu próximo proyecto.</h2>
      <p>Instalaciones, mantenimiento y asesoramiento para encontrar una solución.</p></div>
      <a class="btn light" href="contacto.html">Contactar ↗</a></div></section>'''
    # ABOUT with real company text and real project photos when supplied.
    about_body=f'''<section class="pagehero"><div class="wrap">
       <span class="eyebrow">La empresa</span><h1>Sobre nosotros</h1>
       <p>Conoce nuestra experiencia, nuestra forma de trabajar y las especialidades de {short}.</p></div></section>
       <section class="section" id="sobre-nosotros"><div class="wrap about-grid">
       <div><span class="eyebrow">Nuestra trayectoria</span>
       <h2>{E(info.get("about_title") or "Compromiso con cada instalación.")}</h2>
       <p class="lead">{about}</p>
       <p>{E(info.get("about_more") or "Ofrecemos atención y soluciones adaptadas a las necesidades de cada proyecto. Contacta con nosotros para ampliar información sobre nuestros servicios.")}</p>
       <a class="btn" href="contacto.html">Hablar con nosotros ↗</a></div>
       <img class="about-photo" src="{secondary}" alt="Fotografía ilustrativa del sector" loading="lazy"></div></section>
       <section class="section soft"><div class="wrap"><span class="eyebrow">Nuestra actividad</span>
       <h2>Nuestras especialidades</h2><div class="tag-list">{''.join(service_tags)}</div></div></section>'''
    if project_cards:
        about_body+=f'''<section class="section"><div class="wrap">
         <span class="eyebrow">Proyectos</span><h2>Trabajos realizados</h2>
         <div class="project-grid">{''.join(project_cards[:3])}</div></div></section>'''
    # Contact with honest disabled form: not misleadingly labeled a working submission.
    form='''<div class="form-panel"><h2>Envíanos tu consulta</h2>
      <p>Déjanos tus datos y cuéntanos qué necesitas.</p>
      <form class="sample-form" aria-label="Formulario visual de muestra">
      <div class="form-grid">
        <label>Nombre<input type="text" placeholder="Nombre y apellidos" autocomplete="off"></label>
        <label>Teléfono<input type="tel" placeholder="Tu teléfono" autocomplete="off"></label>
      </div>
      <label>Correo electrónico<input type="email" placeholder="tu@email.com" autocomplete="off"></label>
      <label>Mensaje<textarea placeholder="Cuéntanos en qué podemos ayudarte"></textarea></label>
      <div class="form-info">Formulario de demostración: todavía no realiza envíos ni guarda los datos introducidos.</div>
      <button type="button" class="btn demo-form-button" aria-disabled="true">Enviar consulta (muestra)</button>
      </form></div>'''
    contact_body=f'''<section class="pagehero"><div class="wrap">
      <span class="eyebrow">Estamos a tu disposición</span><h1>Contáctanos</h1>
      <p>Solicita información sobre nuestros servicios y proyectos.</p></div></section>
      <section class="section" id="contacto"><div class="wrap contact-grid"><div>
      <span class="eyebrow">Datos de contacto</span><h2>Hablemos de tu proyecto.</h2>
      <p>Estamos a tu disposición para responder consultas de instalaciones y mantenimiento.</p>
      <div class="contact-panel">
      <div class="contact-line"><small>Teléfono</small>{phone_html}</div>
      <div class="contact-line"><small>Correo electrónico</small><a href="mailto:{email}">{email}</a></div>
      {address_html}{hours_html}</div></div>{form}</div></section>'''
    result={'index.html':page('index.html','Inicio',home),
            'sobre-nosotros.html':page('sobre-nosotros.html','Sobre nosotros',about_body),
            'contacto.html':page('contacto.html','Contáctanos',contact_body)}
    assert 'Una web clara' not in result['index.html']
    assert 'Una empresa que merece presentarse bien' not in result['index.html']
    assert '02 · Una web para conectar' not in result['index.html']
    assert 'Teléfono' in result['index.html'] and email in result['index.html']
    assert '<footer ' in result['index.html']
    assert 'Visitar sitio original' not in ''.join(result.values())
    assert 'Formulario de demostración' in result['contacto.html']
    return result
