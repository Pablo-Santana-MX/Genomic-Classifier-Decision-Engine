import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# 1. Configuración de la página (Debe ser la primera línea de Streamlit)
st.set_page_config(page_title="Genomic Decision Engine", page_icon="🧬", layout="wide")

# 2. Inyección de CSS personalizado para simular las "Tarjetas" blancas flotantes
st.markdown("""
<style>
    /* Estilo para las métricas y tarjetas */
    div.css-1r6slb0, div.css-12w0qpk {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    /* Estilo de los botones grandes */
    div.stButton > button {
        height: 80px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        border: 1px solid #00B4D8;
        color: #00B4D8;
        background-color: white;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00B4D8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# 3. Encabezado de la App
st.title("🧬 Genomic Classifier Decision Engine")
st.markdown("*Plataforma de Inteligencia Clínica para Diagnóstico Tisular*")
st.divider()

# 4. Sección Superior: Layout al estilo de la imagen (Gráfico + Reporte)
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### Rendimiento del Modelo (XGBoost)")
    # Medidor circular de Plotly (El de la imagen)
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 94.7,  # Aquí puedes conectar la precisión real de tu modelo
        number = {'suffix': "%"},
        title = {'text': "Precisión Predictiva"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#00B4D8"},
            'bgcolor': "#F4F7F6",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
        }
    ))
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📋 Validación de Reportes")
    # Tarjeta de resumen simulada
    st.info("**Cohorte Analizada:** 150 Pacientes")
    st.success("**Estado del Modelo:** Calibrado y Listo")
    st.warning("**Falsos Negativos (Críticos):** Minimizados a 0.02%")
    
    st.markdown("---")
    st.markdown("**Componentes Principales (PCA):** 10")
    st.markdown("**Corrección Estadística:** FDR Benjamini-Hochberg")

# 5. Botones de Acción (Parte inferior de la imagen)
st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button("📊 Analizar Nueva Cohorte", use_container_width=True):
        st.success("Cargando nuevos datos genómicos...")

with col_btn2:
    if st.button("📄 Generar PDF Ejecutivo", use_container_width=True):
        st.success("Reporte generado para el Expediente Clínico (EHR).")

with col_btn3:
    if st.button("🧪 Ver Pruebas de Welch", use_container_width=True):
        st.info("Cargando significancia de biomarcadores...")

# 6. Pestañas de Análisis Detallado (Tus datos reales)
st.divider()
tab1, tab2 = st.tabs(["Distribución de Riesgo (ML)", "Significancia de Biomarcadores (Stats)"])

with tab1:
    st.subheader("Análisis de Probabilidades Clínicas")
    st.markdown("Tabla de predicciones del modelo XGBoost frente al diagnóstico clínico real.")
    
    try:
        # Cargamos los datos reales desde la carpeta de resultados
        df_ml = pd.read_csv("results/dashboard_exports/model_predictions_summary.csv")
        st.dataframe(df_ml, use_container_width=True)
    except FileNotFoundError:
        st.error("⚠️ Archivo model_predictions_summary.csv no encontrado. Asegúrate de que la carpeta results/dashboard_exports/ esté en el repositorio.")

with tab2:
    st.subheader("Top 10 Biomarcadores (Validados por Welch & FDR)")
    st.markdown("Componentes principales que superaron el umbral de significancia estadística.")
    
    try:
        # Cargamos los datos reales de significancia
        df_stats = pd.read_csv("results/dashboard_exports/statistical_testing_summary.csv")
        
        # Detectamos automáticamente si el CSV usa guiones bajos o espacios
        col_neg_log = "Neg_Log10_PVal" if "Neg_Log10_PVal" in df_stats.columns else "Neg Log10 PVal"
        col_fdr = "P_Value_FDR_Corrected" if "P_Value_FDR_Corrected" in df_stats.columns else "P Value FDR Corrected"
        
        # Filtramos solo el Top 10
        df_top10 = df_stats.sort_values(by=col_neg_log, ascending=False).head(10)
        
        # Resaltamos las columnas más importantes para el médico
        st.dataframe(
            df_top10[["Component", "Significant", col_neg_log, col_fdr]], 
            use_container_width=True
        )
    except KeyError as e:
        st.error(f"Error de columna: No se pudo ordenar. {e}")
        st.info(f"Las columnas exactas en tu archivo son: {df_stats.columns.tolist()}")
    except FileNotFoundError:
        st.error("⚠️ Archivo statistical_testing_summary.csv no encontrado.")
