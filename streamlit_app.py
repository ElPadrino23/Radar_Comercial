import glob
import os

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Radar Comercial - PPG", layout="wide")


def acceso_autorizado():
    password = st.secrets.get("SOC_PASSWORD")
    if not password:
        st.warning("SOC_PASSWORD no esta configurada en los secrets de la app - acceso sin contraseña.")
        return True

    if st.session_state.get("autenticado"):
        return True

    ingresado = st.text_input("Contraseña del equipo SOC", type="password")
    if not ingresado:
        return False
    if ingresado == password:
        st.session_state["autenticado"] = True
        return True

    st.error("Contraseña incorrecta")
    return False


if not acceso_autorizado():
    st.stop()

st.title("Radar Comercial — Detecciones PPG")
st.caption("Resultados de la búsqueda automática en Facebook Marketplace (se actualiza ~1 vez por semana)")

archivos = sorted(glob.glob("results/*.csv"))

if not archivos:
    st.info("Todavía no hay resultados publicados. La búsqueda automática corre semanalmente vía GitHub Actions.")
    st.stop()

partes = []
for archivo in archivos:
    df = pd.read_csv(archivo)
    df["archivo_origen"] = os.path.basename(archivo)
    partes.append(df)

datos = pd.concat(partes, ignore_index=True)

col1, col2 = st.columns(2)
with col1:
    filtro_lugar = st.text_input("Filtrar por lugar (contiene)")
with col2:
    filtro_texto = st.text_input("Filtrar por texto del perfil (contiene)")

filtrados = datos.copy()
if filtro_lugar:
    filtrados = filtrados[filtrados["Lugar"].str.contains(filtro_lugar, case=False, na=False)]
if filtro_texto:
    filtrados = filtrados[filtrados["Nombre del perfil"].str.contains(filtro_texto, case=False, na=False)]

st.write(f"{len(filtrados)} detecciones")
st.dataframe(filtrados, use_container_width=True)

st.download_button(
    "Descargar CSV filtrado",
    filtrados.to_csv(index=False).encode("utf-8"),
    "detecciones_filtradas.csv",
    "text/csv",
)
