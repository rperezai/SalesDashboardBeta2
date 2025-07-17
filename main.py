
import streamlit as st
import pandas as pd
import altair as alt
from PIL import Image

# Branding
logo = Image.open("logo_aquagold.png")
st.image(logo, width=200)

st.title("Dashboard de Ventas – Aquagold")

# Cargar archivo
st.sidebar.header("Subir archivo Excel")
uploaded_file = st.sidebar.file_uploader("Selecciona el archivo .xlsx", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("Archivo cargado correctamente.")

        # Limpiar y procesar
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=[df.columns[0]])  # eliminar filas vacías

        # Detectar columnas
        nombre_vendedor = df.columns[0]
        metricas = df.columns[1:]

        # Separar FCL y Libras
        df_fcl = df[[nombre_vendedor] + [c for c in metricas if "FCL" in c]]
        df_libras = df[[nombre_vendedor] + [c for c in metricas if "LBS" in c]]

        # Convertir a formato largo para análisis
        df_fcl_melt = df_fcl.melt(id_vars=[nombre_vendedor], var_name="Mes", value_name="FCL")
        df_libras_melt = df_libras.melt(id_vars=[nombre_vendedor], var_name="Mes", value_name="Libras")

        # Tabs
        tab1, tab2, tab3 = st.tabs(["📦 Ventas en FCL", "⚖️ Ventas en Libras", "📊 Reporte Gerencial"])

        with tab1:
            st.subheader("Resumen por FCL")
            st.dataframe(df_fcl_melt)

            chart_fcl = alt.Chart(df_fcl_melt).mark_bar().encode(
                x="Mes:N",
                y="FCL:Q",
                color=nombre_vendedor,
                tooltip=[nombre_vendedor, "Mes", "FCL"]
            ).properties(width=700)
            st.altair_chart(chart_fcl, use_container_width=True)

        with tab2:
            st.subheader("Resumen por Libras")
            st.dataframe(df_libras_melt)

            chart_lbs = alt.Chart(df_libras_melt).mark_area(opacity=0.5).encode(
                x="Mes:N",
                y="Libras:Q",
                color=nombre_vendedor,
                tooltip=[nombre_vendedor, "Mes", "Libras"]
            ).properties(width=700)
            st.altair_chart(chart_lbs, use_container_width=True)

        with tab3:
            st.subheader("Análisis Gerencial")
            resumen = df_libras_melt.groupby(nombre_vendedor)["Libras"].sum().reset_index().sort_values("Libras", ascending=False)
            top_vendedor = resumen.iloc[0]

            st.markdown(f"**Top vendedor:** {top_vendedor[nombre_vendedor]} con {top_vendedor['Libras']:.0f} libras vendidas.")
            st.markdown("**Recomendación:** Incentivar a los vendedores con desempeño constante y detectar caídas en la curva mensual.")
            st.markdown("**Blindspot común:** Vendedores con un buen mes aislado que elevan su promedio anual. Validar consistencia mensual.")
            st.dataframe(resumen)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo de ventas en formato Excel.")
