import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# =========================================================================
# 1. CONFIGURACIÓN DEL LAYOUT DE STREAMLIT (Ancho de pantalla completa)
# =========================================================================
st.set_page_config(page_title="Productividad Médica - Virrey Solís", layout="wide")

# Configuración estética de los gráficos
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10, 'axes.labelsize': 11, 'axes.titlesize': 13})


# =========================================================================
# 2. SIMULACIÓN DE DATOS (Representación de la plataforma operativa)
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
# 3. PROCESAMIENTO Y CREACIÓN DE COMPONENTES GRÁFICOS
# =========================================================================

# --- GRÁFICO 1: Productividad Individual (Columna T) ---
META_PRODUCCION = 150
df_medicos = df_mes.groupby('Columna_T').agg(
    Citas_Efectivas=('Columna_D', lambda x: (x == 'Realizada').sum())
).reset_index().sort_values(by='Citas_Efectivas', ascending=False)

df_medicos['Porcentaje'] = (df_medicos['Citas_Efectivas'] / META_PRODUCCION) * 100

def asignar_color(pct):
    if pct >= 95: return '#2ecc71' # Verde
    elif pct >= 85: return '#f1c40f' # Amarillo
    return '#e74c3c' # Rojo

colores_semaforo = df_medicos['Porcentaje'].apply(asignar_color).tolist()

fig_prod, ax_prod = plt.subplots(figsize=(10, 5))
bars = ax_prod.bar(df_medicos['Columna_T'], df_medicos['Citas_Efectivas'], color=colores_semaforo, edgecolor='black', alpha=0.8)
ax_prod.axhline(y=META_PRODUCCION, color='blue', linestyle='--', linewidth=2, label=f'Meta Institutional ({META_PRODUCCION})')
ax_prod.set_title('Productividad Individual por Médico\n(Verde: Óptimo | Amarillo: Aceptable | Rojo: Bajo Rendimiento)', pad=15)
ax_prod.set_ylabel('Citas Realizadas Exitosamente')
ax_prod.set_xlabel('Médico (Columna T)')
plt.setp(ax_prod.get_xticklabels(), rotation=15, ha='right')
ax_prod.set_ylim(0, max(df_medicos['Citas_Efectivas']) + 30)

for bar, pct in zip(bars, df_medicos['Porcentaje']):
    yval = bar.get_height()
    ax_prod.text(bar.get_x() + bar.get_width()/2.0, yval + 3, f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')

ax_prod.legend(loc='lower right')
plt.tight_layout()


# --- GRÁFICO 2: Análisis Geográfico de Anulaciones ---
df_geografico = df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia'])].groupby('Localidad').size().reset_index(name='Total_Anulaciones').sort_values(by='Total_Anulaciones', ascending=False)

fig_geo, ax_geo = plt.subplots(figsize=(10, 5))
sns.barplot(data=df_geografico, x='Total_Anulaciones', y='Localidad', palette='Reds_r', edgecolor='black', ax=ax_geo)
ax_geo.set_title('Zonas Críticas - Volumen de Inasistencias y Cancelaciones por Localidad', pad=15)
ax_geo.set_xlabel('Cantidad de Novedades Registradas')
ax_geo.set_ylabel('Sector / Localidad de Bogotá')
plt.tight_layout()


# --- GRÁFICO 3: Diagrama de Pareto de Motivos (Columna D) ---
df_motivos = df_mes[df_mes['Motivo_Detallado'] != 'N/A'].groupby('Motivo_Detallado').size().reset_index(name='Cantidad').sort_values(by='Cantidad', ascending=False)
df_motivos['Porcentaje_Acumulado'] = (df_motivos['Cantidad'].cumsum() / df_motivos['Cantidad'].sum()) * 100

fig_pareto, ax1 = plt.subplots(figsize=(11, 5))
ax1.bar(df_motivos['Motivo_Detallado'], df_motivos['Cantidad'], color='#34495e', edgecolor='black', alpha=0.85)
ax1.set_title('Análisis Causa Raíz (Pareto) de Anulación de Consultas', pad=15)
ax1.set_ylabel('Frecuencia (Cantidad de Casos)', color='#34495e')
ax1.set_xlabel('Motivos de Cancelación / Inasistencia (Derivados de Columna D)')
ax1.tick_params(axis='y', labelcolor='#34495e')
plt.setp(ax1.get_xticklabels(), rotation=20, ha='right')

ax2 = ax1.twinx()
ax2.plot(df_motivos['Motivo_Detallado'], df_motivos['Porcentaje_Acumulado'], color='#e67e22', marker='D', linewidth=2, label='% Acumulado')
ax2.set_ylabel('Porcentaje Acumulado (%)', color='#e67e22')
ax2.tick_params(axis='y', labelcolor='#e67e22')
ax2.set_ylim(0, 105)
plt.tight_layout()


# =========================================================================
# 4. INTERFAZ GRÁFICA Y DEPLIEGUE EN STREAMLIT
# =========================================================================
st.title("TABLERO DE CONTROL: PRODUCTIVIDAD MÉDICA")
st.markdown("### Monitoreo mensual del rendimiento humano y ausentismo en atención en casa — Virrey Solís IPS")
st.write("---")

# Renderizar Módulo II
st.subheader("Módulo II: Desempeño Individual de Profesionales")
st.pyplot(fig_prod)
st.write("---")

# Renderizar Módulo III y IV lado a lado en columnas
st.subheader("Análisis de Pérdida de Productividad (Novedades de la Columna D)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Módulo III: Distribución Geográfica en Bogotá")
    st.pyplot(fig_geo)

with col2:
    st.markdown("#### Módulo IV: Causa Raíz de Cancelaciones")
    st.pyplot(fig_pareto)