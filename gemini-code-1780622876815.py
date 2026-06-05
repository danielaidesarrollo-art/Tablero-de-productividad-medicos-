import pandas as pd
import numpy as np
import streamlit as st

# =========================================================================
# 1. CONFIGURACIÓN DEL ENTORNO DE TRABAJO
# =========================================================================
st.set_page_config(page_title="Productividad Médica - Virrey Solís IPS", layout="wide")

st.title("TABLERO DE CONTROL: PRODUCTIVIDAD MÉDICA")
st.markdown("### Monitoreo Avanzado de Rendimiento Humano y Ausentismo en Atención Domiciliaria")
st.write("---")

# =========================================================================
# 2. COMPONENTE DE CARGA DE DATOS (INPUT)
# =========================================================================
st.sidebar.header("Control de Datos")
archivo_cargado = st.sidebar.file_uploader(
    "Carga el reporte operativo de la plataforma (Excel o CSV)", 
    type=["xlsx", "xls", "csv"]
)

@st.cache_data
def cargar_datos_demo():
    """Genera datos de simulación si el usuario no ha cargado un archivo propio"""
    np.random.seed(42)
    n_registros = 1000
    medicos = ['Dr. Camilo Andrés Soler', 'Dra. María Paula Gómez', 'Dr. Juan Carlos Neira', 'Dra. Sandra Milena Rojas', 'Dr. Diego Alejandro Marín']
    estados_cita = ['Realizada', 'Realizada', 'Realizada', 'Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional']
    motivos_cancelacion = ['Paciente no estaba en casa', 'Paciente rechazó atención', 'Médico con retraso en ruta', 'Reagendamiento institucional', 'Clima / Tránsito']
    localidades = ['Suba', 'Usaquén', 'Kennedy', 'Engativá', 'Bosa', 'Fontibón', 'Chapinero']
    
    datos = {
        'Fecha': pd.date_range(start='2026-05-01', periods=n_registros, freq='h'),
        'Columna_D': np.random.choice(estados_cita, size=n_registros, p=[0.70, 0.10, 0.10, 0.04, 0.04, 0.02]),
        'Columna_T': np.random.choice(medicos, size=n_registros),
        'Localidad': np.random.choice(localidades, size=n_registros),
        'Motivo_Detallado': np.random.choice(motivos_cancelacion, size=n_registros)
    }
    df = pd.DataFrame(datos)
    df.loc[df['Columna_D'] == 'Realizada', 'Motivo_Detallado'] = 'N/A'
    return df

# Lógica de selección de origen de datos
if archivo_cargado is not None:
    try:
        if archivo_cargado.name.endswith('.csv'):
            df_operativo = pd.read_csv(archivo_cargado)
        else:
            df_operativo = pd.read_excel(archivo_cargado)
        st.sidebar.success("¡Archivo cargado con éxito!")
    except Exception as e:
        st.sidebar.error(f"Error al leer el archivo: {e}")
        df_operativo = cargar_datos_demo()
else:
    st.sidebar.info("Visualizando datos de demostración. Carga un archivo para ver tus métricas reales.")
    df_operativo = cargar_datos_demo()

# Validar la existencia de las columnas críticas antes de procesar
if 'Columna_D' not in df_operativo.columns or 'Columna_T' not in df_operativo.columns:
    st.error("El archivo cargado debe contener obligatoriamente las columnas nombradas exactamente como 'Columna_D' (Estados) y 'Columna_T' (Médicos).")
    st.info("Estructurando con datos de demostración debido a incompatibilidad de columnas.")
    df_operativo = cargar_datos_demo()


# =========================================================================
# 3. FILTRADO Y PROCESAMIENTO MÓDULO I (KPIs GLOBALES)
# =========================================================================
# Asegurar formato de fecha para la segmentación mensual táctica
if 'Fecha' in df_operativo.columns:
    df_operativo['Fecha'] = pd.to_datetime(df_operativo['Fecha'])
    meses_disponibles = df_operativo['Fecha'].dt.strftime('%Y-%m').unique()
    mes_seleccionado = st.sidebar.selectbox("Seleccionar Mes de Análisis", opciones=meses_disponibles)
    df_mes = df_operativo[df_operativo['Fecha'].dt.strftime('%Y-%m') == mes_seleccionado].copy()
else:
    df_mes = df_operativo.copy()

# Cálculos de Alto Nivel
total_programadas = len(df_mes)
total_realizadas = len(df_mes[df_mes['Columna_D'] == 'Realizada'])
total_anuladas = len(df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional'])])

tasa_efectividad = (total_realizadas / total_programadas) * 100 if total_programadas > 0 else 0
tasa_ausentismo = (total_anuladas / total_programadas) * 100 if total_programadas > 0 else 0

# Despliegue de Tarjetas de Resumen
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Visitas Programadas", f"{total_programadas} citas")
kpi2.metric("Tasa de Efectividad Global", f"{tasa_efectividad:.1f}%")
kpi3.metric("Tasa de Ausentismo/Cancelación", f"{tasa_ausentismo:.1f}%")
st.write("---")


# =========================================================================
# 4. MÓDULO II: RENDIMIENTO INDIVIDUAL (Columna T)
# =========================================================================
st.subheader("Módulo II: Nivel de Producción Individual por Profesional (Columna T)")

df_medicos = df_mes.groupby('Columna_T').agg(
    Citas_Programadas=('Columna_D', 'count'),
    Citas_Realizadas=('Columna_D', lambda x: (x == 'Realizada').sum())
).sort_values(by='Citas_Realizadas', ascending=False)

# Gráfico nativo para evaluación rápida de productividad del equipo de salud
st.bar_chart(df_medicos['Citas_Realizadas'], use_container_width=True)

# Vista de datos crudos detallada para auditoría de la jefatura médica
with st.expander("Ver tabla detallada de cumplimiento por médico"):
    st.dataframe(df_medicos, use_container_width=True)


# =========================================================================
# 5. MÓDULO III Y IV: ANÁLISIS GEOGRÁFICO Y CAUSA RAÍZ (Columna D)
# =========================================================================
st.write("---")
st.subheader("Análisis de Pérdida de Productividad (Métricas de la Columna D)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Módulo III: Sectores con Mayor Tasa de Inasistencia / Cancelación")
    if 'Localidad' in df_mes.columns:
        df_geografico = df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia'])].groupby('Localidad').size().to_frame(name='Total_Novedades')
        st.bar_chart(df_geografico, y="Total_Novedades", use_container_width=True)
    else:
        st.caption("Agrega una columna llamada 'Localidad' en tu archivo para activar este módulo.")

with col2:
    st.markdown("#### Módulo IV: Motivos Predominantes de Anulación")
    # Desglose de los motivos de anulación derivados del estado de la Columna D
    columna_motivo = 'Motivo_Detallado' if 'Motivo_Detallado' in df_mes.columns else 'Columna_D'
    df_motivos = df_mes[df_mes[columna_motivo] != 'Realizada'].groupby(columna_motivo).size().to_frame(name='Cantidad_Casos')
    st.bar_chart(df_motivos, y="Cantidad_Casos", use_container_width=True)