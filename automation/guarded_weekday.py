#!/usr/bin/env python3
"""Punto de entrada obligatorio de captación: protección anti-reenvío.

Se envuelve el generador sin modificar su código. No tiene ninguna acción
de envío de correo a empresas; únicamente genera borradores. La comprobación
duplica el bloqueo antes de seleccionar, antes de crear una web y antes de
preparar un mensaje comercial.
"""
import sys
import prospecting_weekdays as original
from commercial_email_guard import (
    read_ledger, check_already_emailed, blocked_by_prior_contacts, run_tests,
)

def check_blocked(company, ledger):
    return blocked_by_prior_contacts(company)[0] or check_already_emailed(company, ledger)[0]

def main():
    # If the ledger is missing/corrupt, fail closed and do not even draft emails.
    history = read_ledger()
    if '--demo-test' in sys.argv:
        run_tests()
        assert check_blocked({'name':'Bonela Integra SL'},history)
        assert not check_blocked({
            'name':'EMPRESA NO EXISTENTE DE PRUEBA XX99',
            'website':'https://empresa-ejemplo-pruebas-xx99.es',
        },history)
    choose_original=original.candidate
    extract_original=original.extract
    mail_original=original.create_mail

    def candidate_protected(row,city,cfg,prev):
        company=choose_original(row,city,cfg,prev)
        if company is None or check_blocked(company,history):
            return None
        return company

    def extract_protected(company,cfg):
        result=extract_original(company,cfg)
        if result is None or check_blocked(result,history):
            return None
        return result

    def create_mail_protected(company,link):
        if check_blocked(company,history):
            raise ValueError('CORREO BLOQUEADO: la empresa ya figura como contactada, enviada o incierta')
        return mail_original(company,link)

    original.candidate=candidate_protected
    original.extract=extract_protected
    original.create_mail=create_mail_protected
    original.main()

if __name__=='__main__':
    main()
