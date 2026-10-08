"""Pymatec: presentación en tres páginas de las demos estáticas.

Inicio / Sobre nosotros / Contáctanos. Datos empresariales solo de la web
verificada; nunca activa envíos reales ni muestra enlaces a la web original.
"""
from bs4 import BeautifulSoup
from html import escape

EXTRA_CSS = """
.toplinks{display:flex;gap:25px;align-items:center}
.toplinks a{font-size:14px;font-weight:760;color:#344450;transition:color .2s}
.toplinks a:hover,.toplinks a[aria-current="page"]{color:var(--brand)}
.subhero{min-height:300px;padding:80px 0;color:white;display:flex;align-items:center;background:linear-gradient(90deg,#193a47db,#193a4782),url('https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=1800&q=80') center/cover}
.subhero .eyebrow{color:#dcebf2}.subhero h1{font-size:clamp(40px,6vw,75px);line-height:1.05;letter-spacing:-.065em;margin:15px 0 10px}
.subhero p{max-width:640px;font-size:18px}
.cta-strip{padding:58px 0;background:#eff5f5}
.cta-strip .wrap{display:flex;align-items:center;justify-content:space-between;gap:30px}
.cta-strip h2{font-size:clamp(28px,3.6vw,44px);letter-spacing:-.05em;margin:7px 0 0}
.contact-layout{display:grid;grid-template-columns:.86fr 1.14fr;gap:30px;align-items:start}
.form-shell{background:#fff;padding:34px;border:1px solid #dee7e9;box-shadow:0 20px 42px #2036440f;border-radius:26px}
.contact-layout .contact{padding:29px;background:#f6f7f5;border-radius:24px}
.contact-layout .entry{grid-template-columns:105px 1fr;align-items:start}
.form-shell .sample-form{border:none;padding:0;margin:0}
.form-shell .sample-form h3{font-size:25px;line-height:1.25;margin-bottom:20px}
.form-shell .sample-form .formhelp{background:#eaf4f6;padding:13px;border-radius:13px}
.form-shell .sample-form button{opacity:.83}
.contact-intro{text-align:left;margin-bottom:42px}
.contact-intro h2{font-size:clamp(34px,4.4vw,59px);letter-spacing:-.06em;line-height:1.12;margin:12px 0}
.contact-intro p{color:var(--muted);max-width:630px}
.about-services{padding:70px 0;background:#f7f8f7}
.about-services h2{font-size:clamp(30px,4vw,50px);letter-spacing:-.06em}
.about-tags{display:flex;gap:12px;flex-wrap:wrap}
.about-tags span{border:1px solid #dce6e7;background:white;border-radius:40px;padding:11px 19px;font-weight:740;color:#374c56}
.home-preview{display:flex;align-items:center;gap:22px;margin-top:24px}
.home-preview .button{flex-shrink:0}
@media(max-width:880px){nav{flex-wrap:wrap;padding:10px 0}.toplinks{order:3;width:100%;justify-content:space-between;gap:8px;padding-bottom:10px;display:flex}.toplinks a{font-size:12px}.contact-layout{grid-template-columns:1fr}.cta-strip .wrap{display:block}.cta-strip .button{margin-top:20px}}
@media(max-width:520px){nav{gap:10px}.button{padding:12px 15px;font-size:13px}.logo{max-height:40px;max-width:145px}.toplinks{gap:5px}.form-shell{padding:20px}.subhero{min-height:260px;padding:56px 0}.contact-layout .entry{grid-template-columns:1fr;gap:5px}}
"""

def _clone(markup):
    return BeautifulSoup(markup, 'html.parser')

def _new(soup, markup):
    return _clone(markup).find()

def _configure_links(soup, selected):
    nav = soup.select_one('header nav')
    if nav is None:
        raise ValueError('No se encontró navegación')
    old_links = nav.select_one('.toplinks')
    if old_links: old_links.decompose()
    links = soup.new_tag('div', attrs={'class':'toplinks'})
    for filename, title in (('index.html','Inicio'),('sobre-nosotros.html','Sobre nosotros'),('contacto.html','Contáctanos')):
        tag = soup.new_tag('a',href=filename)
        tag.string = title
        if selected == filename: tag['aria-current'] = 'page'
        links.append(tag)
    button = nav.select_one('a.button')
    if button:
        button['href']='contacto.html'
        button.insert_before(links)
    else:
        nav.append(links)
    for a in soup.select('a[href]'):
        link=a.get('href','')
        if link=='#contacto': a['href']='contacto.html'
        elif link=='#sobre-nosotros': a['href']='sobre-nosotros.html'
        elif link=='#servicios' and selected != 'index.html': a['href']='index.html#servicios'
    logo=nav.select_one('div')
    # preserve original logo and make it a home link if possible
    if logo and logo.name=='div' and not logo.select_one('a'):
        home=soup.new_tag('a',href='index.html')
        for node in list(logo.contents): home.append(node.extract())
        logo.append(home)
    # Links back to the business's original website are intentionally omitted
    for a in soup.select('footer a'):
        a.unwrap()
    foot=soup.select_one('footer')
    if foot:
        foot.clear()
        foot.append('Maqueta de diseño no oficial creada por Pymatec. Sin relación ni aprobación de la empresa. Imágenes ilustrativas y formulario no operativo.')
    return soup

def make_pages(info, city, slug, document):
    """Return {'index.html':..., 'sobre-nosotros.html':..., 'contacto.html':...}."""
    original = _clone(document)
    if not original.select_one('#sobre-nosotros') or not original.select_one('#contacto'):
        raise ValueError('Faltan secciones de origen para generar las páginas')
    style=original.select_one('style')
    if not style: raise ValueError('Falta CSS base')
    style.append(EXTRA_CSS)
    for el in original.select('.contact .entry'):
        if 'web oficial' in el.get_text(' ',strip=True).lower():
            el.decompose()
    name = escape(info['name'])
    genre = escape(city)
    sector = escape(info.get('craft','').replace('_',' ').capitalize())
    # HOME: portada, servicios y adelanto de empresa, sin sección completa ni contacto.
    home = _clone(str(original))
    for selector in ('#sobre-nosotros','#contacto'):
        block=home.select_one(selector)
        if block: block.decompose()
    home = _configure_links(home,'index.html')
    preview = home.select_one('main > section.section:not(#servicios)')
    if preview:
        h2=preview.select_one('h2')
        if h2: h2.string='Una empresa que merece presentarse bien.'
        p=preview.select_one('p')
        if p: p.string='Una web clara y visual que facilita descubrir la trayectoria, los servicios y los datos de contacto.'
        wrap=preview.select_one('.wrap')
        if wrap: wrap.append(_new(home,'<div class="home-preview"><a class="button" href="sobre-nosotros.html">Conoce la empresa ↗</a><a href="contacto.html" class="section-link">Contacta con nosotros</a></div>'))
    # ABOUT: an independent page with the verified paragraph from the company.
    about = _clone(str(original))
    about_section = about.select_one('#sobre-nosotros')
    about_html = str(about_section)
    main=about.select_one('main')
    main.clear()
    hero=f'''<section class="subhero"><div class="wrap"><div class="eyebrow">Conoce la empresa</div><h1>Sobre nosotros.</h1><p>Trayectoria y especialidades de {name}.</p></div></section>'''
    main.append(_new(about,hero))
    main.append(_new(about,about_html))
    services=info.get('services',[])[:8]
    if not services:
        services = [info.get('activity') or ('Servicios de '+sector.lower())]
    cleanservices=''.join('<span>'+escape(str(x)[:80])+'</span>' for x in services)
    main.append(_new(about,'<section class="about-services"><div class="wrap"><span class="eyebrow">Áreas de trabajo</span><h2>Nuestras especialidades</h2><div class="about-tags">'+cleanservices+'</div></div></section>'))
    main.append(_new(about,'<section class="cta-strip"><div class="wrap"><div><span class="eyebrow">Contacta con nosotros</span><h2>¿Hablamos de tu proyecto?</h2></div><a class="button" href="contacto.html">Solicitar presupuesto ↗</a></div></section>'))
    about=_configure_links(about,'sobre-nosotros.html')
    if about.title: about.title.string='Sobre nosotros · '+info['name']
    # CONTACT: clean 2-column layout, remove 'Web oficial' and add demo form.
    contact = _clone(str(original))
    original_contact = contact.select_one('#contacto')
    old_form = original_contact.select_one('form.sample-form')
    if not old_form: raise ValueError('No se ha encontrado el formulario')
    form_html=str(old_form)
    phone = info.get('phone','')
    email = info.get('email','')
    phone_number=escape(phone) if phone else 'Consultar por correo'
    phone_el='<a href="tel:'+escape(phone,quote=True)+'">'+phone_number+'</a>' if phone else '<span>Consultar por correo</span>'
    extra=''
    if info.get('address'):
        extra+='<div class="entry"><small>Dirección</small><span>'+escape(info['address'])+'</span></div>'
    if info.get('hours'):
        extra+='<div class="entry"><small>Horario</small><span>'+escape(info['hours'])+'</span></div>'
    contact_section = '''<section class="section" id="contacto"><div class="wrap">
    <div class="contact-intro"><div class="eyebrow">Contáctanos</div><h2>Cuéntanos qué necesitas.</h2>
    <p>Teléfono y correo de contacto para consultas y presupuestos. El formulario es una muestra visual y todavía no realiza envíos.</p></div>
    <div class="contact-layout"><div class="contact">
    <div class="entry"><small>Teléfono</small>'''+phone_el+'''</div>
    <div class="entry"><small>Email</small><a href="mailto:'''+escape(email,quote=True)+'''">'''+escape(email)+'''</a></div>
    '''+extra+'''</div><div class="form-shell">'''+form_html+'''</div></div></div></section>'''
    main=contact.select_one('main')
    main.clear()
    main.append(_new(contact,'<section class="subhero"><div class="wrap"><div class="eyebrow">Estamos a tu disposición</div><h1>Contáctanos.</h1><p>Habla con '+name+' y solicita información sobre sus servicios.</p></div></section>'))
    main.append(_new(contact,contact_section))
    contact=_configure_links(contact,'contacto.html')
    if contact.title: contact.title.string='Contáctanos · '+info['name']
    result={'index.html':str(home),'sobre-nosotros.html':str(about),'contacto.html':str(contact)}
    assert all('<html' in v and '</html>' in v for v in result.values())
    assert 'id="sobre-nosotros"' not in result['index.html']
    assert 'id="contacto"' not in result['index.html']
    assert '<form' in result['contacto.html']
    assert 'Visitar sitio original' not in result['contacto.html']
    return result
