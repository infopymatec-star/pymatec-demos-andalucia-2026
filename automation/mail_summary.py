#!/usr/bin/env python3
"""Comprueba las URLs de la ejecución y envía, solo con credenciales válidas,
un resumen al propietario de Pymatec. NUNCA manda emails a empresas.
No indica 'enviado' si smtp no confirma la transacción.
"""
from __future__ import annotations
import argparse, datetime as dt, json, os, smtplib, ssl, sys, time
from email.message import EmailMessage
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'automation'/'reports'
TO_DEFAULT='joselss86@hotmail.com'
FROM_EXPECTED='info.pymatec@gmail.com'

def validate_public(url):
    """GitHub Pages can take time to show latest deploy. A 200 alone is not enough."""
    if not url.startswith('https://infopymatec-star.github.io/pymatec-demos-andalucia-2026/auto-demos/'):
        return False, 'URL no pertenece al repositorio'
    try:
        page=requests.get(url,timeout=12,headers={'Cache-Control':'no-cache'})
        if page.status_code!=200:return False,f'HTTP {page.status_code}'
        if 'site-footer' not in page.text or 'noindex' not in page.text:
            return False,'La versión publicada no tiene los elementos requeridos'
        return True,'ok'
    except requests.RequestException as exc:
        return False,type(exc).__name__

def build_text(data):
    lines=[
        f'Pymatec · Captación web · {data["date"]}',
        f'Área: {data.get("city","Málaga provincia")}',
        f'Empresas verificadas: {len(data["entries"])} de 5 previstas.',
        'Objetivo: 2 sin web localizada y 3 con web mejorable, completando con otra categoría si fuese necesario.',
        'Empresas excluidas: TOPdigital/TDconsulting y coincidencias registradas.',
        '',
    ]
    for i,e in enumerate(data['entries'],1):
        status='PÚBLICA VERIFICADA' if e.get('verified_public') else 'ENLACE NO VERIFICADO - NO COMPARTIR'
        lines += [f'{i}. {e["name"]} · {e.get("activity","")} · {e.get("city","")}',
        f'   Sitio previo: {e.get("verified_url") or "No localizado; verificar antes de afirmar inexistencia"}',
        f'   Propuesta: {e.get("demo_url","")}',
        f'   Email: {e.get("email") or "No encontrado"}',
        f'   Publicación: {status}',
        '   Correo comercial: PREPARADO (NO ENVIADO)',
        f'   Observaciones: {", ".join(e.get("website_signals",[])) or e.get("site_evidence","Revisión de información pública")}',
        '']
    if not data['entries']:
        lines += ['No se generaron propuestas con evidencias suficientes hoy. No se inventaron datos.','']
    if data.get('limitations'):
        lines += ['Incidencias:']+['- '+x for x in data['limitations'][:15]]
    lines += ['',
        'El informe puede llegar DESPUÉS de las 08:37, porque antes deben completarse la investigación, la publicación y las comprobaciones.',
        'Ningún correo comercial se envía automáticamente a empresas. Los correos públicos no autorizan publicidad no solicitada (LSSI, art. 21).',
        'Registro histórico: https://github.com/infopymatec-star/pymatec-demos-andalucia-2026/tree/main/automation/reports',
        ]
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--demo-test',action='store_true')
    parser.add_argument('--date',default=dt.datetime.now(ZoneInfo('Europe/Madrid')).date().isoformat())
    args=parser.parse_args()
    if args.demo_test:
        b=build_text({'date':'2026-10-09','city':'Málaga','entries':[{'name':'Ejemplo','activity':'Climatización','city':'Málaga','demo_url':'https://example.org/'}]})
        assert 'NO ENVIADO' in b and 'Ejemplo' in b
        print('MAIL_TEST_OK: solo compone resumen, no contacta ni envía')
        return
    name=REPORT/(args.date+'.json')
    if not name.exists():raise FileNotFoundError(name)
    data=json.loads(name.read_text(encoding='utf-8'))
    for entry in data.get('entries',[]):
        for attempt in range(4):
            ok,reason=validate_public(entry.get('demo_url',''))
            if ok:break
            if attempt<3:time.sleep(12)
        entry['verified_public']=ok
        entry['publish_reason']=reason
    data['status']='public_verified' if all(e.get('verified_public') for e in data['entries']) else 'incomplete'
    data['checked_at']=dt.datetime.now(ZoneInfo('Europe/Madrid')).isoformat(timespec='seconds')
    name.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    sender=os.getenv('PYMATEC_GMAIL_ADDRESS','').strip()
    password=os.getenv('PYMATEC_GMAIL_APP_PASSWORD','').strip()
    recipient=os.getenv('PYMATEC_REPORT_RECIPIENT',TO_DEFAULT).strip()
    if not sender or not password:
        print('EMAIL_RESUMEN_PENDIENTE: falta credencial SMTP de Gmail en los secretos de GitHub. Registro en Reports/JSON.')
        return
    if sender.lower()!=FROM_EXPECTED:
        raise ValueError('La dirección remitente debe ser info.pymatec@gmail.com')
    if recipient.lower()!=TO_DEFAULT:
        raise ValueError('El resumen solo puede enviarse a la dirección propia autorizada: '+TO_DEFAULT)
    msg=EmailMessage()
    msg['From']=sender;msg['To']=recipient
    msg['Subject']=f'Pymatec | resumen captación web {args.date} ({len(data.get("entries",[]))}/5)'
    msg.set_content(build_text(data))
    # TLS y solo el destinatario particular autorizado, nunca ninguno de los prospectos.
    with smtplib.SMTP('smtp.gmail.com',587,timeout=30) as smtp:
        smtp.starttls(context=ssl.create_default_context())
        smtp.login(sender,password)
        smtp.send_message(msg)
    print('RESUMEN_GMAIL_ENVIADO_A_USUARIO: '+recipient)
if __name__=='__main__':main()
