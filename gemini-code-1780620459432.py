import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. CONFIGURACIÓN DE LA APP (Streamlit Interface Core)
# ==============================================================================
st.set_page_config(
    page_title="Productividad Médica - Virrey Solís IPS",
    page_icon="🩺",
    layout="wide"
)

# Renderizado de encabezados en la interfaz web
st.title("🩺 Control de Productividad - Atención Domiciliaria")
st.subheader("Módulo Integrado de Análisis de Talento Humano")
st.markdown("---")


# ==============================================================================
# 2. CAPA DE DATOS (Simulación de la Columna D del Sistema de Información)
# ==============================================================================
@st.cache_data
def extraer_datos_sistema():
    """
    Simula la ingesta mensual de los registros crudos de la Columna D.
    En producción, esta función realizaría la conexión al repositorio del ecosistema.
    """
    data_sistema = {
        'ID_Medico': ['MED-001', 'MED-002', 'MED-003', 'MED-004', 'MED-005', 'MED-006'],
        'Nombre_Medico': ['Carlos Mendoza', 'Diana Restrepo', 'Andrés Felipe Ruiz', 'Elena Santamaría', 'Mauricio Gómez', 'Adriana Lucía'],
        'Programa_Atencion': ['Crónicos', 'Paliativos', 'Atención General', 'Crónicos', 'Paliativos', 'Atención General'],
        # Registros crudos extraídos de la Columna D:
        'Columna_D_Registros_Totales': [135, 120, 105, 85, 140, 118], 
        'Citas_Canceladas_o_Ausentes': [5, 2, 7, 3, 12, 0]
    }
    return pd.DataFrame(data_sistema)


# ==============================================================================
# 3. PIPELINE DE TRANSFORMACIÓN Y REGLAS DE NEGOCIO (Parámetros de Productividad)
# ==============================================================================
def procesar_pipeline_productividad(df_entrada):
    """
    Aplica las reglas de negocio institucionales sobre los datos crudos
    basado en la jornada estándar de 36 horas semanales.
    """
    df = df_entrada.copy()
    
    # Parámetro institucional: Meta óptima para 144 horas mensuales (~45-60 min por visita)
    META_CONSULTAS_MES = 120 
    
    # Depuración de registros: Citas efectivamente ejecutadas
    df['Consultas_Efectivas'] = df['Columna_D_Registros_Totales'] - df['Citas_Canceladas_o_Ausentes']
    
    # Cálculo porcentual de rendimiento
    df['Tasa_Cumplimiento_Pct'] = ((df['Consultas_Efectivas'] / META_CONSULTAS_MES) * 100).round(1)
    
    # Clasificación vectorial de estados (Matriz de Umbrales)
    condiciones = [
        (df['Tasa_Cumplimiento_Pct'] >= 90.0),
        (df['Tasa_Cumplimiento_Pct'] >= 80.0) & (df['Tasa_Cumplimiento_Pct'] < 90.0),
        (df['Tasa_Cumplimiento_Pct'] < 80.0)
    ]
    estados = ['Adecuada', 'En Observación', 'Inadecuada']
    df['Estado_Productividad'] = np.select(condiciones, estados, default='Sin Clasificar')
    
    # Inyección de alertas lógicas para auditoría médica
    def clasificar_alerta(row):
        if row['Estado_Productividad'] == 'Adecuada': 
            return '✅ Rendimiento óptimo en zona asignada.'
        elif row['Estado_Productividad'] == 'En Observación': 
            return '⚠️ Evaluar tiempos de desplazamiento o reprocesos logísticos.'
        else:
            if row['Citas_Canceladas_o_Ausentes'] > 10:
                return '🚨 Crítico: Afectado por alto índice de inasistencia externa.'
            return '🚨 Crítico: Subregistro en Columna D o baja cobertura de agenda.'

    df['Alertas_Auditoria'] = df.apply(clasificar_alerta, axis=1)
    return df


# ==============================================================================
# 4. EJECUCIÓN DEL PROCESAMIENTO
# ==============================================================================
df_crudo = extraer_datos_sistema()
df_procesado = procesar_pipeline_productividad(df_crudo)


# ==============================================================================
# 5. COMPONENTES INTERACTIVOS DE LA INTERFAZ (Sidebar & Filtros)
# ==============================================================================
st.sidebar.header("Filtros del Tablero")
st.sidebar.markdown("Use estos controles para segmentar el análisis mensual.")

programas_disponibles = ['Todos'] + list(df_procesado['Programa_Atencion'].unique())
programa_seleccionado = st.sidebar.selectbox("Seleccione el Programa:", programas_disponibles)

# Filtrado dinámico del dataframe principal
if programa_seleccionado != 'Todos':
    df_filtrado = df_procesado[df_procesado['Programa_Atencion'] == programa_seleccionado]
else:
    df_filtrado = df_procesado


# ==============================================================================
# 6. CAPA VISUAL DE CONTROL (Métricas Globales - KPIs)
# ==============================================================================
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="Total Consultas Efectivas (Mes)", 
        value=int(df_filtrado['Consultas_Efectivas'].sum())
    )
with col2:
    promedio_cumplimiento = df_filtrado['Tasa_Cumplimiento_Pct'].mean()
    st.metric(
        label="Promedio de Cumplimiento Institucional", 
        value=f"{promedio_cumplimiento:.1f}%"
    )
with col3:
    medicos_criticos = len(df_filtrado[df_filtrado['Estado_Productividad'] == 'Inadecuada'])
    st.metric(
        label="Casos de Productividad Inadecuada", 
        value=medicos_criticos, 
        delta="- Revisión Requerida" if medicos_criticos > 0 else "Operación OK",
        delta_color="inverse"
    )

st.markdown("### Reporte Detallado de Desempeño Profesional")


# ==============================================================================
# 7. CAPA DE FORMATO CONDICIONAL (Visualización de Tabla)
# ==============================================================================
def aplicar_estilo_productividad(val):
    """Asigna colores de fondo en la tabla web según el estado determinado."""
    if val == 'Adecuada': 
        return 'background-color: #d4edda; color: #155724; font-weight: bold;' # Verde institucional
    elif val == 'En Observación': 
        return 'background-color: #fff3cd; color: #856404; font-weight: bold;' # Amarillo de control
    elif val == 'Inadecuada': 
        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;' # Rojo de auditoría
    return ''

# Selección y ordenamiento final de las columnas para visualización en el dashboard
columnas_vista = [
    'ID_Medico', 'Nombre_Medico', 'Programa_Atencion', 
    'Consultas_Efectivas', 'Tasa_Cumplimiento_Pct', 
    'Estado_Productividad', 'Alertas_Auditoria'
]
df_vista_final = df_filtrado[columnas_vista]

# Despliegue de la tabla interactiva formateada
st.dataframe(
    df_vista_final.style.map(aplicar_estilo_productividad, subset=['Estado_Productividad']),
    use_container_width=True,
    hide_index=True
)


# ==============================================================================
# 8. PIE DE MÓDULO (Cierre del Ecosistema)
# ==============================================================================
st.info(
    "💡 Nota de Integración: Sistema configurado bajo la regla estándar de 36 horas "
    "semanales para el servicio médico. Los datos mostrados corresponden al procesamiento "
    "automatizado de la Columna D del corte mensual."
)