import pandas as pd
import numpy as np
import streamlit as st

# =========================================================================
# 1. CONFIGURACIÓN DE LA INTERFAZ
# =========================================================================
st.set_page_config(page_title="Productividad Médica - Virrey Solís IPS", layout="wide")

st.title("TABLERO DE CONTROL: PRODUCTIVIDAD MÉDICA")
st.markdown("### Monitoreo de Rendimiento Humano y Ausentismo en Atención Domiciliaria")
st.write("---")

# =========================================================================
# 2. CARGA DE DATOS REALES VS DEMOSTRACIÓN
# =========================================================================
st.sidebar.header("Control de Datos")
archivo_cargado = st.sidebar.file_uploader(
    "Carga el reporte operativo de la plataforma (Excel o CSV)", 
    type=["xlsx", "xls", "csv"]
)

@st.cache_data
def cargar_datos_demo():
    """Genera datos simulados estructurados con los encabezados reales de tu tabla"""
    np.random.seed(42)
    n_registros = 1000
    medicos_demo = ['Dr. Camilo Andrés Soler', 'Dra. María Paula Gómez', 'Dr. Juan Carlos Neira', 'Dra. Sandra Milena Rojas', 'Dr. Diego Alejandro Marín']
    estados_demo = ['Realizada', 'Realizada', 'Realizada', 'Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional']
    localidades_demo = ['Suba', 'Usaquén', 'Kennedy', 'Engativá', 'Bosa', 'Fontibón', 'Chapinero']
    
    datos = {
        'FECHA': pd.date_range(start='2026-05-01', periods=n_registros, freq='h'),
        'Mes': '2026-05',
        'MEDICO': np.random.choice(medicos_demo, size=n_registros),
        'OBSERVACION DOMI': np.random.choice(estados_demo, size=n_registros, p=[0.72, 0.10, 0.10, 0.04, 0.02, 0.02]),
        'BARRIO-LOCALIDAD': np.random.choice(localidades_demo, size=n_registros)
    }
    return pd.DataFrame(datos)

# Procesar archivo cargado por el usuario o usar la demo
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
    st.sidebar.info("Visualizando datos de demostración. Carga tu archivo para ver métricas reales.")
    df_operativo = cargar_datos_demo()

# =========================================================================
# 3. MAPEADO Y VALIDACIÓN DE ENCABEZADOS REALES
# =========================================================================
# Forzar a mayúsculas los nombres de las columnas cargadas para evitar errores de digitación
df_operativo.columns = [c.strip() for c in df_operativo.columns]

columnas_requeridas = ['MEDICO', 'OBSERVACION DOMI', 'BARRIO-LOCALIDAD']
validas = all(col in df_operativo.columns for col in columnas_requeridas)

if not validas:
    st.error("El archivo cargado no coincide plenamente con los encabezados esperados.")
    st.info("Asegúrate de que tu archivo incluya las columnas: 'MEDICO', 'OBSERVACION DOMI' y 'BARRIO-LOCALIDAD'.")
    df_operativo = cargar_datos_demo()

# Segmentación mensual
if 'Mes' in df_operativo.columns:
    meses_disponibles = df_operativo['Mes'].unique()
    mes_seleccionado = st.sidebar.selectbox("Seleccionar Mes de Análisis", options=meses_disponibles)
    df_mes = df_operativo[df_operativo['Mes'] == mes_seleccionado].copy()
elif 'FECHA' in df_operativo.columns:
    df_operativo['FECHA'] = pd.to_datetime(df_operativo['FECHA'])
    df_operativo['Mes'] = df_operativo['FECHA'].dt.strftime('%Y-%m')
    meses_disponibles = df_operativo['Mes'].unique()
    mes_seleccionado = st.sidebar.selectbox("Seleccionar Mes de Análisis", options=meses_disponibles)
    df_mes = df_operativo[df_operativo['Mes'] == mes_seleccionado].copy()
else:
    df_mes = df_operativo.copy()

# =========================================================================
# 4. MÓDULO I: KPIs GLOBALES
# =========================================================================
total_programadas = len(df_mes)
total_realizadas = len(df_mes[df_mes['OBSERVACION DOMI'] == 'Realizada'])
total_anuladas = len(df_mes[df_mes['OBSERVACION DOMI'].isin(['Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional'])])

tasa_efectividad = (total_realizadas / total_programadas) * 100 if total_programadas > 0 else 0
tasa_ausentismo = (total_anuladas / total_programadas) * 100 if total_programadas > 0 else 0

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Visitas Programadas", f"{total_programadas} citas")
kpi2.metric("Tasa de Efectividad Global", f"{tasa_efectividad:.1f}%")
kpi3.metric("Tasa de Ausentismo/Cancelación", f"{tasa_ausentismo:.1f}%")
st.write("---")

# =========================================================================
# 5. MÓDULO II: RENDIMIENTO INDIVIDUAL (Columna MEDICO)
# =========================================================================
st.subheader("Módulo II: Nivel de Producción Individual por Profesional")

df_medicos = df_mes.groupby('MEDICO').agg(
    Programadas=('OBSERVACION DOMI', 'count'),
    Efectivas=('OBSERVACION DOMI', lambda x: (x == 'Realizada').sum())
).sort_values(by='Efectivas', ascending=False)

st.bar_chart(df_medicos['Efectivas'], use_container_width=True)

with st.expander("Ver tabla detallada de auditoría médica"):
    st.dataframe(df_medicos, use_container_width=True)

# =========================================================================
# 6. MÓDULO III Y IV: ANÁLISIS GEOGRÁFICO Y MOTIVOS (OBSERVACION DOMI)
# =========================================================================
st.write("---")
st.subheader("Análisis de Pérdida de Productividad")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Módulo III: Sectores con Mayor Tasa de Inasistencia / Cancelación")
    # Filtramos las citas que no pudieron concretarse con éxito
    df_no_efectivas = df_mes[df_mes['OBSERVACION DOMI'].isin(['Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional'])]
    if not df_no_efectivas.empty:
        df_geografico = df_no_efectivas.groupby('BARRIO-LOCALIDAD').size().to_frame(name='Total Novedades')
        st.bar_chart(df_geografico, y="Total Novedades", use_container_width=True)
    else:
        st.success("No se registran cancelaciones ni inasistencias en el mes seleccionado.")

with col2:
    st.markdown("#### Módulo IV: Motivos Predominantes de Anulación")
    # Desglose causal basado en los registros cargados en OBSERVACION DOMI
    df_motivos = df_mes[df_mes['OBSERVACION DOMI'] != 'Realizada'].groupby('OBSERVACION DOMI').size().to_frame(name='Cantidad de Casos')
    if not df_motivos.empty:
        st.bar_chart(df_motivos, y="Cantidad_Casos" if "Cantidad_Casos" in df_motivos.columns else "Cantidad de Casos", use_container_width=True)
    else:
        st.success("Cero incidencias operativas en la agenda.")