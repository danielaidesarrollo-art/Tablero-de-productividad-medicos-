import pandas as pd
import numpy as np
import streamlit as st

# =========================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =========================================================================
st.set_page_config(page_title="Productividad Médica - Virrey Solís", layout="wide")

st.title("TABLERO DE CONTROL: PRODUCTIVIDAD MÉDICA")
st.markdown("### Monitoreo mensual del rendimiento humano y ausentismo — Virrey Solís IPS")
st.write("---")

# =========================================================================
# 2. SIMULACIÓN DE DATOS REQUERIDOS (Columnas T y D)
# =========================================================================
np.random.seed(42)
n_registros = 1000

medicos = [
    'Dr. Camilo Andrés Soler', 'Dra. María Paula Gómez', 
    'Dr. Juan Carlos Neira', 'Dra. Sandra Milena Rojas', 
    'Dr. Diego Alejandro Marín'
]
estados_cita = [
    'Realizada', 'Realizada', 'Realizada', 
    'Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional'
]
motivos_cancelacion = [
    'Paciente no estaba en casa', 'Paciente rechazó atención', 
    'Médico con retraso en ruta', 'Reagendamiento institucional', 'Clima / Tránsito'
]
localidades = ['Suba', 'Usaquén', 'Kennedy', 'Engativá', 'Bosa', 'Fontibón', 'Chapinero']

datos_simulados = {
    'Fecha': pd.date_range(start='2026-05-01', periods=n_registros, freq='h'),
    'Columna_D': np.random.choice(estados_cita, size=n_registros, p=[0.70, 0.10, 0.10, 0.04, 0.04, 0.02]),
    'Columna_T': np.random.choice(medicos, size=n_registros),
    'Localidad': np.random.choice(localidades, size=n_registros),
    'Motivo_Detallado': np.random.choice(motivos_cancelacion, size=n_registros)
}

df_operativo = pd.DataFrame(datos_simulados)
df_operativo.loc[df_operativo['Columna_D'] == 'Realizada', 'Motivo_Detallado'] = 'N/A'

# Filtrado Mensual (Mayo 2026)
df_mes = df_operativo[df_operativo['Fecha'].dt.strftime('%Y-%m') == '2026-05'].copy()


# =========================================================================
# 3. MÓDULO II: RENDIMIENTO INDIVIDUAL (Columna T)
# =========================================================================
st.subheader("Módulo II: Desempeño Individual de Profesionales (Columna T)")

df_medicos = df_mes.groupby('Columna_T').agg(
    Citas_Efectivas=('Columna_D', lambda x: (x == 'Realizada').sum())
)

# Renderizado del gráfico nativo de barras para los médicos
st.bar_chart(df_medicos, y="Citas_Efectivas", use_container_width=True)


# =========================================================================
# 4. MÓDULO III Y IV: ANÁLISIS DE NOVEDADES (Columna D)
# =========================================================================
st.write("---")
st.subheader("Análisis de Pérdida de Productividad (Variables de la Columna D)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Módulo III: Distribución Geográfica de Inasistencias/Cancelaciones")
    df_geografico = df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia'])].groupby('Localidad').size().to_frame(name='Total_Novedades')
    
    # Gráfico nativo para las localidades
    st.bar_chart(df_geografico, y="Total_Novedades", use_container_width=True)

with col2:
    st.markdown("#### Módulo IV: Motivos Predominantes de Anulación")
    df_motivos = df_mes[df_mes['Motivo_Detallado'] != 'N/A'].groupby('Motivo_Detallado').size().to_frame(name='Casos')
    
    # Gráfico nativo para las causas raíz
    st.bar_chart(df_motivos, y="Casos", use_container_width=True)