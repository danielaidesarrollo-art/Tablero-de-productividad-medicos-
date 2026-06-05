import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PLATAFORMA DIGITAL (Streamlit Settings)
# ==============================================================================
st.set_page_config(
    page_title="Productividad Médica Domiciliaria - Virrey Solís IPS",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Tablero de Control de Productividad Médica")
st.subheader("Análisis de Rendimiento de Talento Humano y Logística Domiciliaria")
st.markdown("---")


# ==============================================================================
# 2. CAPA DE ENTRADA DE DATOS (Ingesta y Simulación Base)
# ==============================================================================
@st.cache_data
def ingestar_datos_cierre_mensual():
    # Base de Médicos y Registros de la Columna D
    medicos_data = {
        'ID_Medico': ['MED-001', 'MED-002', 'MED-003', 'MED-004', 'MED-005', 'MED-006'],
        'Nombre_Medico': ['Carlos Mendoza', 'Diana Restrepo', 'Andrés Felipe Ruiz', 'Elena Santamaría', 'Mauricio Gómez', 'Adriana Lucía'],
        'Programa_Atencion': ['Crónicos', 'Paliativos', 'Atención General', 'Crónicos', 'Paliativos', 'Atención General'],
        'Columna_D_Registros_Totales': [135, 120, 112, 88, 140, 118], 
        'Citas_Anuladas': [5, 2, 7, 3, 35, 0] # MED-005 simulado con alta inasistencia externa
    }
    df_medicos = pd.DataFrame(medicos_data)
    
    # Registro de Cancelaciones (Geografía e Historial de Motivos)
    cancelaciones_data = {
        'Localidad_Bogota': ['Kennedy', 'Suba', 'Bosa', 'Engativá', 'Kennedy', 'Suba', 'Bosa', 'Usaquén', 'Ciudad Bolívar', 'Kennedy'],
        'Motivo_Anulacion': [
            'Paciente ausente en domicilio', 'Paciente ausente en domicilio', 
            'Hospitalización previa reportada', 'Rechazo del servicio por cuidador',
            'Paciente ausente en domicilio', 'Falla logística (Dirección errónea)', 
            'Paciente ausente en domicilio', 'Rechazo del servicio por cuidador',
            'Hospitalización previa reportada', 'Paciente ausente en domicilio'
        ],
        'Frecuencia_Eventos': [45, 30, 25, 20, 18, 12, 10, 8, 7, 5]
    }
    df_cancelaciones = pd.DataFrame(cancelaciones_data)
    
    return df_medicos, df_cancelaciones

df_crudo_medicos, df_crudo_cancelaciones = ingestar_datos_cierre_mensual()


# ==============================================================================
# 3. PIPELINE DE TRANSFORMACIÓN DE PRODUCTIVIDAD (Reglas de Negocio)
# ==============================================================================
def ejecutar_pipeline_analitica(df_medicos):
    df = df_medicos.copy()
    META_BASE_MENSUAL = 120 # Derivado de la jornada de 36 horas semanales
    
    # Consultas efectivas ejecutadas en domicilio
    df['Consultas_Efectivas'] = df['Columna_D_Registros_Totales'] - df['Citas_Anuladas']
    df['Tasa_Cumplimiento_Pct'] = ((df['Consultas_Efectivas'] / META_BASE_MENSUAL) * 100).round(1)
    
    # Clasificación por Umbrales Automatizados
    condiciones = [
        (df['Tasa_Cumplimiento_Pct'] >= 90.0),
        (df['Tasa_Cumplimiento_Pct'] >= 80.0) & (df['Tasa_Cumplimiento_Pct'] < 90.0),
        (df['Tasa_Cumplimiento_Pct'] < 80.0)
    ]
    estados = ['Adecuada', 'En Observación', 'Inadecuada']
    df['Estado_Productividad'] = np.select(condiciones, estados, default='Sin Clasificar')
    
    # Alertas de Gestión de Auditoría
    def asignar_alerta(row):
        if row['Estado_Productividad'] == 'Adecuada':
            return '✅ Rendimiento óptimo en zona asignada.'
        elif row['Estado_Productividad'] == 'En Observación':
            return '⚠️ Evaluar tiempos de desplazamiento o reprocesos logísticos.'
        else:
            if row['Citas_Anuladas'] > 15:
                return '🚨 Crítico: Afectado severamente por ausentismo del paciente.'
            return '🚨 Crítico: Baja cobertura de agenda o subregistro en Columna D.'
            
    df['Alertas_Auditoria'] = df.apply(asignar_alerta, axis=1)
    return df

df_medicos_procesado = ejecutar_pipeline_analitica(df_crudo_medicos)


# ==============================================================================
# 4. COMPONENTES INTERACTIVOS DE SEGMENTACIÓN (Sidebar)
# ==============================================================================
st.sidebar.header("Filtros del Ecosistema")
st.sidebar.markdown("Establezca los parámetros de visualización mensual.")

programa_filtro = st.sidebar.selectbox(
    "Seleccione el Programa Clínico:",
    ['Todos'] + list(df_medicos_procesado['Programa_Atencion'].unique())
)

if programa_filtro != 'Todos':
    df_medicos_filtrado = df_medicos_procesado[df_medicos_procesado['Programa_Atencion'] == programa_filtro]
else:
    df_medicos_filtrado = df_medicos_procesado


# ==============================================================================
# 5. CAPA VISUAL 1: TARJETAS DE CONTROL (Métricas Consolidadas)
# ==============================================================================
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric(
        label="Consultas Efectivas Totales", 
        value=int(df_medicos_filtrado['Consultas_Efectivas'].sum())
    )
with m_col2:
    promedio_cumplimiento = df_medicos_filtrado['Tasa_Cumplimiento_Pct'].mean()
    st.metric(
        label="Promedio Rendimiento Médico", 
        value=f"{promedio_cumplimiento:.1f}%"
    )
with m_col3:
    total_agendadas = df_medicos_filtrado['Columna_D_Registros_Totales'].sum()
    total_anuladas = df_medicos_filtrado['Citas_Anuladas'].sum()
    tasa_cancelacion = (total_anuladas / total_agendadas * 100) if total_agendadas > 0 else 0
    st.metric(
        label="Tasa de Cancelación Global", 
        value=f"{tasa_cancelacion:.1f}%"
    )
with m_col4:
    casos_criticos = len(df_medicos_filtrado[df_medicos_filtrado['Estado_Productividad'] == 'Inadecuada'])
    st.metric(
        label="Productividades Inadecuadas", 
        value=casos_criticos,
        delta="- Alerta de Gestión" if casos_criticos > 0 else "Estable",
        delta_color="inverse"
    )

st.markdown("---")


# ==============================================================================
# 6. CAPA VISUAL 2: DESEMPEÑO INDIVIDUAL DEL TALENTO HUMANO
# ==============================================================================
st.subheader("1. Evaluación de Desempeño y Productividad Individual")

def estilar_tabla_productividad(val):
    if val == 'Adecuada': 
        return 'background-color: #d4edda; color: #155724; font-weight: bold;'
    elif val == 'En Observación': 
        return 'background-color: #fff3cd; color: #856404; font-weight: bold;'
    elif val == 'Inadecuada': 
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'
    return ''

columnas_mostrar = [
    'ID_Medico', 'Nombre_Medico', 'Programa_Atencion', 
    'Consultas_Efectivas', 'Tasa_Cumplimiento_Pct', 
    'Estado_Productividad', 'Alertas_Auditoria'
]

st.dataframe(
    df_medicos_filtrado[columnas_mostrar].style.map(estilar_tabla_productividad, subset=['Estado_Productividad']),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")


# ==============================================================================
# 7. CAPA VISUAL 3: GEOGRAFÍA Y ANÁLISIS DE MOTIVOS DE CANCELACIÓN
# ==============================================================================
st.subheader("2. Distribución Logística y Fugas de Productividad Domiciliaria")

geo_col1, geo_col2 = st.columns(2)

with geo_col1:
    st.markdown("#### Concentración Geográfica de Inasistencias (Sectores Críticos)")
    # Consolidado por Localidad
    df_geo_summary = df_crudo_cancelaciones.groupby('Localidad_Bogota')['Frecuencia_Eventos'].sum().reset_index()
    df_geo_summary = df_geo_summary.sort_values(by='Frecuencia_Eventos', ascending=False)
    
    st.dataframe(
        df_geo_summary.rename(columns={'Localidad_Bogota': 'Localidad / Sector', 'Frecuencia_Eventos': 'Número de Cancelaciones'}),
        use_container_width=True,
        hide_index=True
    )
    st.caption("📍 Priorizar auditoría de asignación de rutas y coberturas en las primeras localidades listadas.")

with geo_col2:
    st.markdown("#### Pareto de Motivos Predominantes de Anulación")
    # Consolidado por Causa
    df_motivos_summary = df_crudo_cancelaciones.groupby('Motivo_Anulacion')['Frecuencia_Eventos'].sum().reset_index()
    df_motivos_summary['Porcentaje'] = ((df_motivos_summary['Frecuencia_Eventos'] / df_motivos_summary['Frecuencia_Eventos'].sum()) * 100).round(1)
    df_motivos_summary = df_motivos_summary.sort_values(by='Frecuencia_Eventos', ascending=False)
    
    st.dataframe(
        df_motivos_summary.rename(columns={'Motivo_Anulacion': 'Causa Determinada', 'Frecuencia_Eventos': 'Casos', 'Porcentaje': '% del Total'}),
        use_container_width=True,
        hide_index=True
    )
    st.caption("💡 Las causales administrativas o logísticas internas requieren intervención inmediata en el agendamiento.")


# ==============================================================================
# 8. PIE DE PÁGINA (Posicionamiento Técnico del Módulo)
# ==============================================================================
st.markdown("---")
st.info(
    "⚙️ Módulo de Cierre de Ecosistema Digital | Virrey Solís IPS. "
    "Procesamiento ejecutado sobre la base histórica consolidada de la Columna D. "
    "Parámetros calibrados según jornada laboral médica reglamentaria de 36 horas semanales."
)