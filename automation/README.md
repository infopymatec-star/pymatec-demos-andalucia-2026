# Automatización diaria gratuita · Pymatec

- **Programa:** `automation/free_daily.py` (Python, sin OpenAI API ni servicios de pago).
- **Programación:** `.github/workflows/pymatec-free-daily.yml` a las 09:23 de Europe/Madrid.
- **Publicación:** GitHub Pages, bajo `auto-demos/`.
- **Informe diario:** `automation/reports/AAAA-MM-DD.md` y GitHub Issues.
- **Resultado:** hasta cinco maquetas no oficiales por día, solo si se puede confirmar la web original y su email.
- **Propuestas:** cada carpeta `auto-demos/<empresa>/propuesta-email.txt` contiene un texto de email. El informe incluye enlace que **abre el redactor de Gmail**, pero **no crea automáticamente un borrador real en Gmail ni envía correo**.
- **Evitar repeticiones:** `automation/seen.json` guarda los dominios.
- **Identidad:** intenta extraer logo desde el sitio web de cada empresa y color `theme-color`; si no lo encuentra, usa texto corporativo y una paleta orientativa del sector, sin fingir que es el logo o color oficial.
- **Búsqueda:** una petición moderada diaria al servicio público Overpass/OpenStreetMap. Este servicio puede limitar solicitudes y recomienda infraestructura propia para uso comercial; por tanto, los resultados **no están garantizados**. No se usan fuentes de datos de pago.
- **Privacidad/publicidad:** repositorio y maquetas **públicos**. El correo público de una empresa no constituye consentimiento para email comercial; revisar artículo 21 LSSI antes de enviar.
- **Costes:** GitHub Actions con runners estándar en un repositorio público y GitHub Pages son gratuitos según su documentación actual, sujetos a condiciones y límites. No contratar planes ni añadir tarjeta.
- **Caducidad:** si GitHub desactiva workflows `schedule` tras 60 días sin actividad, reactivar desde Actions.
- **Pruebas:** `python automation/free_daily.py --demo-test`.

**Ninguna comunicación sale automáticamente a empresas.**