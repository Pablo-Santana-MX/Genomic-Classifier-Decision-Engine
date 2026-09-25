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
        st.error(f"Error de columna: {e}")
        st.info(f"Las columnas exactas en tu archivo son: {df_stats.columns.tolist()}")
    except FileNotFoundError:
        st.error("⚠️ Archivo statistical_testing_summary.csv no encontrado.")
