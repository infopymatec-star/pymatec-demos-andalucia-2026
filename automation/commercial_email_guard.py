#!/usr/bin/env python3
"""Bloqueo de repetición de correos comerciales Pymatec.

NINGUNA función de este módulo envía emails.
Este historial de envíos es distinto del historial de webs analizadas.
Regla: un máximo de un correo comercial por empresa en toda su historia,
independientemente de destinatarios, dominios o variaciones del nombre.

Antes de cualquier envío *futuro y legalmente autorizado* se debe revisar
también Gmail/Enviados para todos los emails y alias conocidos.
Si no se puede comprobar el historial de Gmail, NO enviar.
"""
from __future__ import annotations
import argparse, json, re, unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/'automation'/'commercial_email_history.json'
EXCLUDED=ROOT/'automation'/'excluded_companies.json'
GENERIC_MAIL_DOMAINS={
 'gmail.com','googlemail.com','hotmail.com','outlook.com','outlook.es',
 'live.com','live.es','yahoo.com','yahoo.es','icloud.com','msn.com',
 'protonmail.com','proton.me','aol.com','orange.es','telefonica.net',
}
BLOCK_STATUSES={'sent','sending','reserved','uncertain','unknown'}
LEGAL_SUFFIX=r'(?:\s+(?:s\.?\s*l\.?\s*u?\.?|s\.?\s*a\.?\s*u?\.?|s\.?\s*c\.?|s\.?\s*c\.?\s*a\.?|sociedad\s+limitada|sociedad\s+anonima))+$'

def clean(value):
    value=unicodedata.normalize('NFKD',str(value or ''))
    value=''.join(ch for ch in value if not unicodedata.combining(ch)).lower()
    return re.sub(r'\s+',' ',value.strip())

def company_name_key(name):
    name=clean(name).replace('&',' y ')
    name=re.sub(r'[^a-z0-9\s]',' ',name)
    name=re.sub(r'\s+',' ',name).strip()
    name=re.sub(r'\s+(?:s\s*l\s*u?|s\s*a\s*u?|s\s*c\s*a?|sociedad limitada|sociedad anonima)$','',name).strip()
    return name

def dom(site):
    s=(site or '').strip()
    if not s:return ''
    if not s.startswith(('https://','http://')):s='https://'+s
    host=(urlparse(s).hostname or '').lower()
    return host.removeprefix('www.')

def company_identifiers(company):
    """Fail-closed match: alias/nombre, dominio web, dominio de email corporativo,
    emails exactos e identificadores OSM. Un alias detectado bloquea toda empresa.
    """
    result=set()
    for name in [company.get('name'),*(company.get('aliases') or [])]:
        v=company_name_key(name)
        if v:result.add('name:'+v)
    for web in [company.get('website'),company.get('verified_url'),company.get('domain'),*(company.get('domains') or [])]:
        d=dom(web)
        if d:result.add('domain:'+d)
    for recipient in [company.get('email'),*(company.get('emails') or [])]:
        email=clean(recipient)
        if '@' in email and ' ' not in email:
            result.add('email:'+email)
            maildomain=email.split('@')[-1]
            if maildomain not in GENERIC_MAIL_DOMAINS:
                result.add('domain:'+maildomain)
    osm=clean(company.get('osm_id'))
    if osm:result.add('osm:'+osm)
    return result

def read_ledger(path=LEDGER):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data,dict) or not isinstance(data.get('records'),list):
        raise ValueError('Historial inválido; bloquear envío hasta resolver')
    return data

def check_already_emailed(company, ledger=None):
    """Return (blocked, reason). Unknown states block (never assume no send)."""
    if ledger is None:ledger=read_ledger()
    keys=company_identifiers(company)
    if not keys:return True,'Identidad no verificable: envío bloqueado'
    for record in ledger.get('records',[]):
        status=clean(record.get('status'))
        if status not in BLOCK_STATUSES:continue
        match=keys & company_identifiers(record)
        if match:
            msg=('Ya enviado; segundo correo bloqueado' if status=='sent'
                 else 'Envío anterior pendiente o incierto: bloquear para evitar duplicado')
            return True,msg+' ('+', '.join(sorted(match))+')'
    return False,'Sin coincidencias en el historial local; NO acredita ausencia de correos en Gmail'

def blocked_by_prior_contacts(company, excluded_path=EXCLUDED):
    try: data=json.loads(Path(excluded_path).read_text(encoding='utf-8'))
    except (OSError,ValueError,TypeError):
        return True,'No se pudo leer exclusiones: no enviar'
    aliases={company_name_key(x) for x in data.get('previously_contacted',[])}
    names={company_name_key(company.get('name'))}
    names.update(company_name_key(x) for x in company.get('aliases',[]))
    if any(x and x in aliases for x in names):
        return True,'Empresa ya tratada o contactada anteriormente'
    return False,''

def preflight(company, *, authorized=False, gmail_sent_checked=False, gmail_no_prior_send=False, ledger=None):
    """A check for a hypothetical manual/legal send. This tool cannot send.
    Caller must perform fresh Gmail sent search for every known email/address,
    verify same-company aliases, and record confirmation after a send.
    Any uncertainty means a hard block.
    """
    if not authorized:
        return False,'Prohibido: no consta base legal para publicidad comercial'
    already,reason=blocked_by_prior_contacts(company)
    if already:return False,reason
    already,reason=check_already_emailed(company,ledger)
    if already:return False,reason
    if not gmail_sent_checked or not gmail_no_prior_send:
        return False,'Bloqueado hasta revisar Gmail/Enviados y confirmar 0 envíos anteriores'
    return True,'Sin duplicados encontrados; la autorización debe ser válida y actual'

def run_tests():
    # Same business: brand spellings, websites, alias domains and different contacts.
    record={'name':'Instalaciones del Sur S.L.','website':'https://www.instalacionesdelsur.es',
       'email':'contacto@instalacionesdelsur.es','aliases':['Instalaciones Sur'],
       'domains':['sur-instalaciones.com'],'status':'sent','gmail_message_id':'test-only-not-real'}
    mock={'records':[record]}
    for c in [
        {'name':'Instalaciones del Sur SL','email':'gerencia@gmail.com'},
        {'name':'Instalaciones Sur','website':'https://otro.com'},
        {'name':'Nueva sociedad','website':'https://sur-instalaciones.com'},
        {'name':'Empresa distinta','email':'administracion@instalacionesdelsur.es'},
        {'name':'Empresa distinta','email':'contacto@instalacionesdelsur.es'},
    ]:
        blocked,reason=check_already_emailed(c,mock)
        assert blocked,('NO BLOQUEADO',c,reason)
    no_hit={'name':'Otra empresa','website':'https://otraempresa.es','email':'info@otraempresa.es'}
    assert not check_already_emailed(no_hit,mock)[0]
    assert not preflight(no_hit,authorized=True,gmail_sent_checked=False,gmail_no_prior_send=True,ledger=mock)[0]
    assert not preflight(no_hit,authorized=False,gmail_sent_checked=True,gmail_no_prior_send=True,ledger=mock)[0]
    assert preflight(no_hit,authorized=True,gmail_sent_checked=True,gmail_no_prior_send=True,ledger=mock)[0]
    unknown={'records':[{**record,'status':'uncertain'}]}
    assert check_already_emailed({'name':'Instalaciones Sur'},unknown)[0]
    assert blocked_by_prior_contacts({'name':'Bonela Integra S.L.'})[0]
    assert check_already_emailed({'name':''},mock)[0]
    print('MAIL_DUPLICATE_GUARD_OK: 1 único envío por empresa, alias/email/dominios, duda bloqueada. No se envió nada.')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--demo-test',action='store_true')
    p.add_argument('--company',default='')
    p.add_argument('--email',default='')
    p.add_argument('--website',default='')
    opt=p.parse_args()
    if opt.demo_test:run_tests()
    else:
        allowed,reason=preflight({'name':opt.company,'email':opt.email,'website':opt.website})
        print('BLOQUEADO' if not allowed else 'REVISAR',reason)
