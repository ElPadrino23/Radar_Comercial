# Radar_Comercial
## Luis Fernando Martinez Barragan / Linkedin.com/in/barraganlf / @lfmbarragan 


## Project Purpose

Radar-Comercial is an automated brand protection monitoring system designed to detect unauthorized sellers of PPG products (PPG, Comex, Pittura, and Chalina) on Facebook Marketplace. The tool uses Selenium WebDriver to perform automated searches, extract seller information, and generate detailed reports in CSV format. By combining keyword matching with coincidence thresholds, the system identifies potential unauthorized distributors and resellers, enabling PPG's compliance team to take swift action against intellectual property violations.

## Expansion Project

Phase 2 of Radar-Comercial will extend monitoring capabilities beyond Marketplace to include Facebook Groups and public feeds, where unauthorized sales activity is most prevalent. The expansion will introduce manual bot functionality with enhanced data extraction (seller contact info, pricing, post dates, location), multi-format export options (JSON, Excel), and anti-detection protections including rate limiting, user-agent rotation, and behavioral randomization. This modular approach allows for future integration of additional platforms and advanced analytics while maintaining compliance and operational stability.

## Credenciales

Las credenciales de Facebook ya NO se guardan en este repositorio. Se configuran como variables de entorno `FB_USUARIO` y `FB_CONTRASENA` (en local, o como Secrets en GitHub Actions). Ver `setup.txt` para más detalle.

> Nota: la cuenta que se usaba antes quedó expuesta en texto plano en commits previos de este repo. Aunque ya se quitó del archivo actual, sigue visible en el historial de git — se recomienda rotar la contraseña de esa cuenta.

## Despliegue para uso del SOC (sin instalar nada)

El proyecto corre de forma automática ~1 vez por semana vía GitHub Actions (`.github/workflows/scrape.yml`), usando la sesión guardada en cookies (secret `FB_COOKIES_B64`) y publicando los resultados en `results/`. El SOC consulta esos resultados desde una app de Streamlit (`streamlit_app.py`) desplegada gratis en [Streamlit Community Cloud](https://streamlit.io/cloud), conectada a este repo — se abre desde el navegador, sin descargar nada.

Secrets necesarios en GitHub (Settings → Secrets and variables → Actions):
- `FB_USUARIO`, `FB_CONTRASENA`: credenciales de la cuenta de Facebook.
- `FB_COOKIES_B64`: contenido de `cookies.pkl` codificado en base64 (`base64 -w0 cookies.pkl`).

Secret necesario en Streamlit Cloud (App settings → Secrets):
- `SOC_PASSWORD`: contraseña compartida para que el equipo del SOC entre a ver los resultados.
