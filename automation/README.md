# Automatización Pymatec · Málaga, días laborables, 08:37

Este repositorio conserva la **última plantilla de referencia revisada**, adaptada para cada empresa.

## Configuración confirmada

- Ejecución GitHub Actions `.github/workflows/pymatec-free-daily.yml`, **lunes a viernes a las 08:37 Europe/Madrid** (`37 8 * * 1-5`). Sábados y domingos no se ejecuta.
- Sin caducidad puesta voluntariamente. `workflow_dispatch` permite reejecución manual.
- La búsqueda rota por **18 municipios de Málaga y provincia**, no por Granada/Sevilla u otras provincias.
- Objetivo de investigación: **2 empresas sin web oficial localizada y 3 con web mejorable**. Si no es posible, se completa con la otra categoría hasta cinco; **no se falsifican cinco** si las evidencias son insuficientes.
- Fuentes: OpenStreetMap/Overpass para descubrir candidatos y sitio web oficial para verificar. Para fichas sin web, una segunda comprobación en resultados públicos es obligatoria y puede fallar; **no se afirma inexistencia absoluta de web**. Las búsquedas son limitadas, no sustituyen una inspección manual.
- Las candidatas con web se consideran *mejorables* **solo si** se detecta al menos una señal técnica concreta, descrita en el informe, y hay un párrafo de actividad + datos de contacto reales. No se infiere antigüedad exacta.
- Sectores: pequeñas empresas de instalaciones, mantenimiento y oficios. Se excluyen ecommerce y casos con información escasa.
- Exclusiones: `automation/excluded_companies.json` incluye **Grupo TOPdigital, TDconsulting**, sus alias y dominios, y algunas empresas ya tratadas. `automation/seen.json` mantiene dominios, nombres, identificadores OSM y correos para evitar repetición.
- Modelo web: `automation/site_pages.py`. **Inicio** solo servicios, proyectos reales cuando se acrediten y llamada a la acción; **Sobre nosotros** aparte; **Contacto** aparte con formulario de muestra inoperativo. Todas con pie de página corporativo. Fotos representativas de sector sin atribuirlas a la empresa. **No se inventan proyectos, testimonios, certificaciones ni años de experiencia.**
- Revisión automatizada antes de publicar: contenido, enlaces internos, imágenes con atributo alt, 3 páginas, texto de la empresa, menú, pie y formulario declarado no operativo. **La revisión visual real en móvil y ordenador requiere inspección adicional**; no se confunde el test HTML con auditoría visual.
- Propuestas: `auto-demos/<slug>/` contiene los tres HTML + `propuesta-email.txt`, redactado de forma personalizada con **presupuesto 490 € + IVA**, dos revisiones, 15 días de incidencias y pago 50/50.
- **Prohibido enviar automáticamente correos comerciales**. Los correos públicos no autorizan publicidad no solicitada (art. 21 LSSI). El estado por defecto es preparado/pendiente de acreditación legal, nunca enviado.
- **Informe:** `automation/reports/AAAA-MM-DD.md` y `.json` con todas las empresas verificadas o los motivos por los que hubo menos de cinco; no se afirma lo no completado.

## Correo diario a su propietario

El workflow `summary` comprueba las URLs tras publicarlas y **puede enviar al correo propio `joselss86@hotmail.com`**, exclusivamente, usando `automation/mail_summary.py`, si se configuran los secretos **`PYMATEC_GMAIL_ADDRESS` = `info.pymatec@gmail.com`** y **`PYMATEC_GMAIL_APP_PASSWORD`** (contraseña de aplicación Google, nunca una contraseña normal ni incluida en código). Configurar en *Repositorio → Settings → Secrets and variables → Actions*.

**Estado inicial del envío: NO CONFIGURADO** hasta confirmar esos secretos. Sin ellos se genera el informe histórico en GitHub, pero **no se envía email**. No se envía correo a prospectos en ningún caso.

**La búsqueda comienza con la programación prevista para las 08:37; el informe solo puede enviarse después de generar, desplegar y comprobar las propuestas**, por lo que su recepción a esa hora exacta no es técnicamente posible en este flujo.

## Continuidad y límites de servicios externos

- GitHub Actions admite zona horaria IANA, pero **no garantiza inicio al segundo**; puede haber retrasos y omisiones por carga. Las fuentes públicas también pueden fallar.
- GitHub puede **desactivar workflows programados de repositorios públicos tras 60 días sin actividad**. Mientras haya nuevos commits diarios del informe, hay actividad, pero no se puede prometer duración indefinida sin supervisión.
- GitHub Pages y los informes en el repositorio son públicos; **no almacenar información privada ni secretos**.
- No es un sistema de CRM de envío masivo. La calidad y legalidad tienen prioridad sobre completar artificialmente el cupo.
- Coste de ejecución con GitHub estándar sujeto a las condiciones y límites de GitHub. No requiere n8n ni API de OpenAI.

## Pruebas sin contactar empresas

```bash
python automation/prospecting_weekdays.py --demo-test
python automation/mail_summary.py --demo-test
```

## Cancelación

Desde GitHub → Actions → `Pymatec - captación web L-V 08:37` → menú (`...`) → *Disable workflow*. No modificar ni detener salvo solicitud expresa del usuario o fallos de seguridad.
