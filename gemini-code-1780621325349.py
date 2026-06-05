import streamlit as st
import pandas as pd
import numpy as np
import io

# ==============================================================================
# 1. CONFIGURACIÓN DEL SISTEMA DIGITAL DE LA IPS
# ==============================================================================
st.set_page_config(
    page_title="Productividad Médica - Virrey Solís IPS",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Tablero de Control de Productividad Médica")
st.subheader("Ecosistema Avanzado de Monitoreo de Atención Domiciliaria")
st.markdown("---")

# ==============================================================================
# 2. CAPA DE EXTRACCIÓN DE DATOS (Simulación de Ingesta desde Columna D)
# ==============================================================================
@st.cache_data
def extraer_datos_operativos():
    # Base unificada de profesionales médicos
    medicos_data = {
        'ID_Medico': ['MED-001', 'MED-002', 'MED-003', 'MED-004', 'MED-005', 'MED-006'],
        'Nombre_Medico': ['Dr. Carlos Mendoza', 'Dra. Diana Restrepo', 'Dr. Andrés Felipe Ruiz', 'Dra. Elena Santamaría', 'Dr. Mauricio Gómez', 'Dra. Adriana Lucía'],
        'Programa_Atencion': ['Crónicos', 'Paliativos', 'Atención General', 'Crónicos', 'Paliativos', 'Atención General'],
        'Columna_D_Agendadas': [135, 120, 112, 88, 140, 118], 
        'Citas_Anuladas': [5, 2, 7, 3, 35, 0]
    }
    
    # Histórico geográfico y causales de cancelaciones en la ciudad
    cancelaciones_data = {
        'Localidad_Bogota': ['Kennedy', 'Suba', 'Bosa', 'Engativá', 'Kennedy', 'Suba', 'Bosa', 'Usaquén', 'Ciudad Bolívar', 'Kennedy'],
        'Motivo_Anulacion': [
            'Paciente ausente en domicilio', 'Paciente ausente en domicilio', 
            'Hospitalización previa reportada', 'Rechazo del servicio por cuidador',
            'Paciente ausente en domicilio', 'Falla logística de la IPS (Dirección)', 
            'Paciente ausente en domicilio', 'Rechazo del servicio por cuidador',
            'Hospitalización previa reportada', 'Paciente ausente en domicilio'
        ],
        'Eventos_Registrados': [45, 32, 25, 20, 18, 12, 10, 8, 7, 5]
    }
    return pd.DataFrame(medicos_data), pd.DataFrame(cancelaciones_data)

df_crudo_medicos, df_crudo_cancelaciones = extraer_datos_operativos()

# ==============================================================================
# 3. PIPELINE DE TRANSFORMACIÓN ANALÍTICA (Backend)
# ==============================================================================
def ejecutar_etl_productividad(df):
    df_out = df.copy()
    META_MENSUAL = 120 # Basado en jornada de 36 horas semanales
    
    # Cálculos operativos de cumplimiento
    df_out['Consultas_Efectivas'] = df_out['Columna_D_Agendadas'] - df_out['Citas_Anuladas']
    df_out['Tasa_Cumplimiento_Pct'] = ((df_out['Consultas_Efectivas'] / META_MENSUAL) * 100).round(1)
    
    # Clasificación Semafórica vectorial
    condiciones = [
        (df_out['Tasa_Cumplimiento_Pct'] >= 90.0),
        (df_out['Tasa_Cumplimiento_Pct'] >= 80.0) & (df_out['Tasa_Cumplimiento_Pct'] < 90.0),
        (df_out['Tasa_Cumplimiento_Pct'] < 80.0)
    ]
    estados = ['Adecuada', 'En Observación', 'Inadecuada']
    df_out['Estado_Productividad'] = np.select(condiciones, estados, default='Sin Clasificar')
    
    # Inyección automática de alertas
    def evaluar_alertas(row):
        if row['Estado_Productividad'] == 'Adecuada': 
            return '✅ Desempeño óptimo en zona operativa.'
        elif row['Estado_Productividad'] == 'En Observación': 
            return '⚠️ Evaluar tiempos de traslado urbano.'
        else: 
            return '🚨 Crítico: Requiere auditoría de Columna D por bajo rendimiento.'
        
    df_out['Alertas_Auditoria'] = df_out.apply(evaluar_alertas, axis=1)
    return df_out

# Corrección de sintaxis aquí (se eliminó la doble asignación errónea)
df_medicos_procesado = ejecutar_etl_productividad(df_crudo_medicos)

# ==============================================================================
# 4. CAPA DE COMPONENTES INTERACTIVOS (Sidebar)
# ==============================================================================
st.sidebar.header("Filtros del Ecosistema")
st.sidebar.markdown("Consolidación mensual de analítica táctica.")

programa_seleccionado = st.sidebar.selectbox(
    "Filtrar por Programa Clínico:",
    ['Todos'] + list(df_medicos_procesado['Programa_Atencion'].unique())
)

if programa_seleccionado == 'Todos':
    df_filtrado = df_medicos_procesado
else:
    df_filtrado = df_medicos_procesado[df_medicos_procesado['Programa_Atencion'] == programa_seleccionado]

# ==============================================================================
# 5. VISUALIZACIÓN: TARJETAS DE MÉTRICAS CORPORATIVAS
# ==============================================================================
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Consultas Efectivas Totales", int(df_filtrado['Consultas_Efectivas'].sum()))
with m2:
    st.metric("Promedio Rendimiento IPS", f"{df_filtrado['Tasa_Cumplimiento_Pct'].mean():.1f}%")
with m3:
    total_agendas = df_filtrado['Columna_D_Agendadas'].sum()
    tasa_cancelacion_global = (df_filtrado['Citas_Anuladas'].sum() / total_agendas * 100) if total_agendas > 0 else 0
    st.metric("Tasa Cancelación Global", f"{tasa_cancelacion_global:.1f}%")
with m4:
    criticos = len(df_filtrado[df_filtrado['Estado_Productividad'] == 'Inadecuada'])
    st.metric("Casos Inadecuados", criticos, delta="- Auditoría Requerida" if criticos > 0 else "OK", delta_color="inverse")

st.markdown("---")

# ==============================================================================
# 6. VISUALIZACIÓN: EVALUACIÓN INDIVIDUAL Y DESCARGAS EXCEL
# ==============================================================================
st.subheader("1. Monitoreo y Desempeño Individual del Personal Médico")

def colorear_tabla(val):
    if val == 'Adecuada': return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == 'En Observación': return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
    elif val == 'Inadecuada': return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
    return ''

columnas_vista = ['ID_Medico', 'Nombre_Medico', 'Programa_Atencion', 'Consultas_Efectivas', 'Tasa_Cumplimiento_Pct', 'Estado_Productividad', 'Alertas_Auditoria']
df_reporte_individual = df_filtrado[columnas_vista]

st.dataframe(
    df_reporte_individual.style.map(colorear_tabla, subset=['Estado_Productividad']),
    use_container_width=True, hide_index=True
)

# Botón de Descarga Nativo a Excel
buffer_excel = io.BytesIO()
with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
    df_reporte_individual.to_excel(writer, index=False, sheet_name='Productividad_Medica')

st.download_button(
    label="📥 Descargar Reporte de Productividad Médica en Excel",
    data=buffer_excel.getvalue(),
    file_name="Reporte_Productividad_Medica_VirreySolis.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")

# ==============================================================================
# 7. VISUALIZACIÓN: PÉRDIDAS LOGÍSTICAS URBANA Y MOTIVOS
# ==============================================================================
st.subheader("2. Distribución Logística de Pérdidas de Agenda Domiciliaria")

col_geo, col_motivo = st.columns(2)

with col_geo:
    st.markdown("#### Identificación Geográfica de Inasistencias (Sectores Críticos)")
    df_geo_summary = df_crudo_cancelaciones.groupby('Localidad_Bogota')['Eventos_Registrados'].sum().reset_index()
    df_geo_summary = df_geo_summary.sort_values(by='Eventos_Registrados', ascending=False)
    st.dataframe(df_geo_summary.rename(columns={'Localidad_Bogota': 'Localidad / Sector', 'Eventos_Registrados': 'Cancelaciones'}), use_container_width=True, hide_index=True)
    
    # Exportación CSV contextual
    buf_geo = io.BytesIO()
    df_geo_summary.to_csv(buf_geo, index=False)
    st.download_button("📥 Descargar Datos Geográficos (CSV)", data=buf_geo.getvalue(), file_name="Fugas_Geograficas_Citas.csv", mime="text/csv")

with col_motivo:
    st.markdown("#### Análisis de Pareto: Motivos Predominantes de Anulación")
    df_motivos_summary = df_crudo_cancelaciones.groupby('Motivo_Anulacion')['Eventos_Registrados'].sum().reset_index()
    df_motivos_summary = df_motivos_summary.sort_values(by='Eventos_Registrados', ascending=False)
    
    # Calcular el porcentaje acumulado manualmente de forma limpia
    total_casos = df_motivos_summary['Eventos_Registrados'].sum()
    df_motivos_summary['% Acumulado'] = ((df_motivos_summary['Eventos_Registrados'].cumsum() / total_casos) * 100).round(1)
    
    st.dataframe(df_motivos_summary.rename(columns={'Motivo_Anulacion': 'Causa de Anulación', 'Eventos_Registrados': 'Casos'}), use_container_width=True, hide_index=True)
    
    # Exportación CSV de motivos
    buf_mot = io.BytesIO()
    df_motivos_summary.to_csv(buf_mot, index=False)
    st.download_button("📥 Descargar Distribución de Motivos (CSV)", data=buf_mot.getvalue(), file_name="Causas_Raiz_Cancelacion.csv", mime="text/csv")

# ==============================================================================
# 8. PIE DE PÁGINA 
# ==============================================================================
st.markdown("---")
st.info("💡 Nota Corporativa: Sistema integrado al cierre del ecosistema digital. Reglas de negocio automatizadas sobre registros unificados de la Columna D.")