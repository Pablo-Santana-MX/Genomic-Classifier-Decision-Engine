"""
Streamlit Dashboard for Genomic Classification
Ejecutar con: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
from fpdf import FPDF

# ==============================================================================
# 1. Page Configuration & Language Dictionary
# ==============================================================================
st.set_page_config(
    page_title="Genomic Classifier Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

LANG = {
    "ES": {
        "title": "Clasificador Genómico para Medicina Personalizada",
        "subtitle": "Evaluación interactiva de modelos XGBoost y significancia de biomarcadores.",
        "context_title": "📖 Contexto y Guía de Uso",
        "context_body": """
        **¿Qué hace esta herramienta?**
        Ingesta datos biológicos, reduce dimensionalidad mediante **PCA**, valida estadísticamente mediante **Pruebas T (FDR)**, y entrena un modelo **XGBoost** para predecir patologías.

        **¿Cómo controlar el dashboard?**
        1. **Filtros:** Aísla cohortes (ej. ver solo donde el modelo falló).
        2. **Rendimiento (ML):** Analiza la distribución del riesgo predictivo.
        3. **Significancia (Stats):** Identifica biomarcadores bajo el umbral $\\alpha = 0.05$.
        
        **📄 Módulo de Exportación PDF:**
        * **¿Qué es?:** Generador dinámico de reportes clínicos estáticos.
        * **¿Para qué sirve?:** Permite exportar los hallazgos del dashboard para adjuntarlos a expedientes clínicos o reportes ejecutivos.
        * **¿Qué reporta?:** KPIs filtrados de la cohorte actual, precisión predictiva y casos de alto riesgo que requieren atención médica inmediata.
        """,
        "sidebar_title": "🧬 IA Biotecnológica",
        "sidebar_filters": "Filtros de Predicción",
        "real_diag": "Diagnóstico Real:",
        "pred_correct": "¿Predicción Correcta?",
        "opt_all": "Todos",
        "opt_success": "Solo Aciertos",
        "opt_error": "Solo Errores",
        "kpi_1": "Pacientes Evaluados",
        "kpi_2": "Precisión del Modelo",
        "kpi_3": "Casos Patológicos",
        "tab_ml": "📊 Rendimiento Predictivo (ML)",
        "tab_stats": "🔬 Significancia Biomarcadores",
        "btn_pdf": "📥 Descargar Reporte Ejecutivo (PDF)",
        "pdf_title": "Reporte de Clasificacion Genomica",
        "error_file": "CSV no encontrados. Ejecuta Notebooks 02 y 03."
    },
    "EN": {
        "title": "Genomic Classifier for Personalized Medicine",
        "subtitle": "Interactive evaluation of XGBoost models and biomarker significance.",
        "context_title": "📖 Context & User Guide",
        "context_body": """
        **What does this tool do?**
        Ingests biological data, reduces dimensionality via **PCA**, validates statistically using **T-Tests (FDR)**, and trains an **XGBoost** model to predict pathologies.

        **How to control the dashboard?**
        1. **Filters:** Isolate cohorts (e.g., view only model errors).
        2. **Performance (ML):** Analyze predictive risk distribution.
        3. **Significance (Stats):** Identify biomarkers below the $\\alpha = 0.05$ threshold.
        
        **📄 PDF Export Module:**
        * **What is it?:** Dynamic generator for static clinical reports.
        * **What is it for?:** Allows exporting dashboard findings to attach them to Electronic Health Records (EHR) or executive summaries.
        * **What does it report?:** Filtered cohort KPIs, predictive accuracy, and high-risk cases requiring immediate medical attention.
        """,
        "sidebar_title": "🧬 Biotech AI",
        "sidebar_filters": "Prediction Filters",
        "real_diag": "Actual Diagnosis:",
        "pred_correct": "Prediction Correct?",
        "opt_all": "All",
        "opt_success": "Successes Only",
        "opt_error": "Errors Only",
        "kpi_1": "Patients Evaluated",
        "kpi_2": "Model Accuracy",
        "kpi_3": "Pathological Cases",
        "tab_ml": "📊 Predictive Performance (ML)",
        "tab_stats": "🔬 Biomarker Significance",
        "btn_pdf": "📥 Download Executive Report (PDF)",
        "pdf_title": "Genomic Classification Report",
        "error_file": "CSV not found. Run Notebooks 02 and 03."
    }
}

# ==============================================================================
# 2. Sidebar & Data Loading
# ==============================================================================
selected_lang = st.sidebar.radio("🌐 Language / Idioma", ["EN", "ES"], horizontal=True)
t = LANG[selected_lang]

st.sidebar.markdown("---")
st.sidebar.title(t["sidebar_title"])

@st.cache_data
def load_data():
    base_dir = Path(__file__).parent.parent
    dash_dir = base_dir / "results" / "dashboard_exports"
    try:
        df_preds = pd.read_csv(dash_dir / "model_predictions_summary.csv")
        df_stats = pd.read_csv(dash_dir / "statistical_testing_summary.csv")
        return df_preds, df_stats
    except FileNotFoundError:
        return pd.DataFrame(), pd.DataFrame()

df_preds, df_stats = load_data()
if df_preds.empty:
    st.error(t["error_file"])
    st.stop()

# ==============================================================================
# 3. Filters & Canvas 
# ==============================================================================
st.sidebar.markdown(f"### {t['sidebar_filters']}")
actual_status = st.sidebar.multiselect(
    t["real_diag"], options=df_preds['Actual_Diagnosis'].unique(), default=df_preds['Actual_Diagnosis'].unique()
)
prediction_correct = st.sidebar.radio(t["pred_correct"], options=[t["opt_all"], t["opt_success"], t["opt_error"]])

df_filtered = df_preds[df_preds['Actual_Diagnosis'].isin(actual_status)]
if prediction_correct == t["opt_success"]:
    df_filtered = df_filtered[df_filtered['Prediction_Correct'] == True]
elif prediction_correct == t["opt_error"]:
    df_filtered = df_filtered[df_filtered['Prediction_Correct'] == False]

st.title(t["title"])
st.markdown(f"*{t['subtitle']}*")

with st.expander(t["context_title"], expanded=True):
    st.markdown(t["context_body"])

# ==============================================================================
# 4. KPIs & PDF Generation
# ==============================================================================
total_patients = len(df_filtered)
accuracy = (df_filtered['Prediction_Correct'].sum() / total_patients) * 100 if total_patients > 0 else 0
high_risk_detected = len(df_filtered[(df_filtered['Actual_Diagnosis'] == 0) & (df_filtered['Prediction_Correct'] == True)])

col1, col2, col3 = st.columns(3)
col1.metric(t["kpi_1"], f"{total_patients}")
col2.metric(t["kpi_2"], f"{accuracy:.1f}%")
col3.metric(t["kpi_3"], f"{high_risk_detected}")

# Función para compilar el PDF
def create_pdf(total, acc, high_risk):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=t["pdf_title"], ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Data Analyst: Pablo Alberto Santana Flores", ln=True, align='L')
    pdf.cell(200, 10, txt="---------------------------------------------------------", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Metric 1: {t['kpi_1']} -> {total}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Metric 2: {t['kpi_2']} -> {acc:.1f}%", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Metric 3: {t['kpi_3']} -> {high_risk}", ln=True, align='L')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Report generated automatically from the Cloud Dashboard.", ln=True, align='L')
    
    return pdf.output(dest="S").encode("latin-1")

pdf_bytes = create_pdf(total_patients, accuracy, high_risk_detected)

st.download_button(
    label=t["btn_pdf"],
    data=pdf_bytes,
    file_name="executive_genomic_report.pdf",
    mime="application/pdf",
    type="primary"
)
st.markdown("---")

# ==============================================================================
# 5. Visualizations (Tabs)
# ==============================================================================
tab1, tab2 = st.tabs([t["tab_ml"], t["tab_stats"]])

with tab1:
    fig_prob = px.histogram(
        df_filtered, x="Prediction_Probability_Pathological", color="Actual_Diagnosis",
        nbins=30, color_discrete_map={0: '#d95f02', 1: '#1b9e77'}, marginal="box"
    )
    st.plotly_chart(fig_prob, use_container_width=True)

with tab2:
    if not df_stats.empty:
        df_stats['Neg_Log_P'] = -np.log10(df_stats['P_Value_FDR_Corrected'])
        fig_stats = px.bar(
            df_stats.sort_values('Neg_Log_P', ascending=True).tail(15),
            x="Neg_Log_P", y="Component", orientation='h', color="Significant",
            color_discrete_map={True: '#d7191c', False: '#bababa'}
        )
        fig_stats.add_vline(x=-np.log10(0.05), line_dash="dash", line_color="blue")
        st.plotly_chart(fig_stats, use_container_width=True)