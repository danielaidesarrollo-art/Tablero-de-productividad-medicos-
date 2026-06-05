import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# =========================================================================
# 1. CONFIGURACIÓN DEL ENTORNO DE RENDERIZADO
# =========================================================================
# Asegura compatibilidad si decides usar .show() más adelante en un navegador
pio.renderers.default = "browser"

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
    'Columna_D': np.random.choice(estados_cita, size=n_registros, p=[0.70, 0.10, 0.10, 0.04, 0.04, 0.02]), # Estados
    'Columna_T': np.random.choice(medicos, size=n_registros), # Nombres de médicos (Columna T)
    'Localidad': np.random.choice(localidades, size=n_registros),
    'Motivo_Detallado': np.random.choice(motivos_cancelacion, size=n_registros)
}

# Crear el DataFrame principal
df_operativo = pd.DataFrame(datos_simulados)

# Limpieza lógica: Si la cita fue 'Realizada', el motivo de cancelación se anula
df_operativo.loc[df_operativo['Columna_D'] == 'Realizada', 'Motivo_Detallado'] = 'N/A'


# =========================================================================
# 3. PROCESAMIENTO DE DATOS Y LÓGICA DE NEGOCIO (BACKEND)
# =========================================================================

# Filtrado Mensual (Ejemplo de análisis táctico: Mayo 2026)
df_mes = df_operativo[df_operativo['Fecha'].dt.strftime('%Y-%m') == '2026-05'].copy()

# A. Cálculo de KPIs Globales del Servicio
total_programadas = len(df_mes)
total_realizadas = len(df_mes[df_mes['Columna_D'] == 'Realizada'])
total_anuladas = len(df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional'])])

tasa_efectividad = (total_realizadas / total_programadas) * 100
tasa_ausentismo = (total_anuladas / total_programadas) * 100

print("=" * 60)
print("     MÉTRICAS CLAVE GENERADAS EN TERMINAL (CONSOLIDADO MENSUAL)     ")
print("=" * 60)
print(f" -> Total Citas Programadas en el Mes : {total_programadas}")
print(f" -> Tasa de Efectividad Global        : {tasa_efectividad:.2f}%")
print(f" -> Tasa de Ausentismo/Cancelación    : {tasa_ausentismo:.2f}%")
print("-" * 60)


# B. Procesamiento de Desempeño Individual (Médicos - Columna T)
# Meta institucional estándar para la jornada del equipo de salud
META_PRODUCCION = 150

df_medicos = df_mes.groupby('Columna_T').agg(
    Citas_Programadas=('Columna_D', 'count'),
    Citas_Efectivas=('Columna_D', lambda x: (x == 'Realizada').sum()),
    Citas_Anuladas=('Columna_D', lambda x: x.isin(['Cancelada por el Usuario', 'Inasistencia', 'Cancelada por el Profesional']).sum())
).reset_index()

df_medicos['Porcentaje_Cumplimiento_Meta'] = (df_medicos['Citas_Efectivas'] / META_PRODUCCION) * 100

# Lógica del Semáforo de Control de Rendimiento Humano
def calcular_semaforo(porcentaje):
    if porcentaje >= 95:
        return '🟢 Óptimo'
    elif porcentaje >= 85:
        return '🟡 Aceptable'
    else:
        return '🔴 Bajo Rendimiento'

df_medicos['Estado_Rendimiento'] = df_medicos['Porcentaje_Cumplimiento_Meta'].apply(calcular_semaforo)


# =========================================================================
# 4. CONSTRUCCIÓN DE COMPONENTES VISUALES (FRONTEND INTERACTIVO)
# =========================================================================

# --- GRAFICO 1: Productividad Individual (Columna T) vs Meta ---
fig_medicos = px.bar(
    df_medicos, 
    x='Columna_T', 
    y='Citas_Efectivas',
    color='Estado_Rendimiento',
    color_discrete_map={'🟢 Óptimo': '#2ecc71', '🟡 Aceptable': '#f1c40f', '🔴 Bajo Rendimiento': '#e74c3c'},
    title='Productividad Individual por Médico vs Estado de Rendimiento (Meta: 150 Realizadas)',
    labels={'Columna_T': 'Médico (Columna T)', 'Citas_Efectivas': 'Citas Realizadas Exitosamente'},
    text='Porcentaje_Cumplimiento_Meta'
)
fig_medicos.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig_medicos.add_hline(y=META_PRODUCCION, line_dash="dash", line_color="blue", annotation_text="Meta Institucional")
fig_medicos.update_layout(yaxis=dict(range=[0, max(df_medicos['Citas_Efectivas']) + 40]))


# --- GRAFICO 2: Análisis Geográfico de Inasistencias y Cancelaciones ---
df_geografico = df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia'])].groupby('Localidad').size().reset_index(name='Total_Anulaciones')
df_geografico = df_geografico.sort_values(by='Total_Anulaciones', ascending=False)

fig_geo = px.bar(
    df_geografico,
    x='Total_Anulaciones',
    y='Localidad',
    orientation='h',
    title='Zonas Críticas: Volumen de Inasistencias y Cancelaciones por Localidad (Bogotá)',
    labels={'Total_Anulaciones': 'Cantidad de Novedades', 'Localidad': 'Sector / Localidad'},
    color='Total_Anulaciones',
    color_continuous_scale='Reds'
)
fig_geo.update_layout(yaxis={'categoryorder':'total ascending'})


# --- GRAFICO 3: Diagrama de Pareto de Motivos de Anulación (Columna D) ---
df_motivos = df_mes[df_mes['Motivo_Detallado'] != 'N/A'].groupby('Motivo_Detallado').size().reset_index(name='Cantidad').sort_values(by='Cantidad', ascending=False)
df_motivos['Porcentaje_Acumulado'] = (df_motivos['Cantidad'].cumsum() / df_motivos['Cantidad'].sum()) * 100

fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
fig_pareto.add_trace(
    go.Bar(x=df_motivos['Motivo_Detallado'], y=df_motivos['Cantidad'], name="Cantidad de Casos", marker_color='#34495e'),
    secondary_y=False
)
fig_pareto.add_trace(
    go.Scatter(x=df_motivos['Motivo_Detallado'], y=df_motivos['Porcentaje_Acumulado'], name="% Acumulado", mode='lines+markers', line_color='#e67e22'),
    secondary_y=True
)
fig_pareto.update_layout(
    title_text="Análisis de Causa Raíz: Motivos Predominantes de Anulación de Consultas",
    xaxis_title="Motivos de Cancelación / Inasistencia (Derivados de Columna D)"
)
fig_pareto.update_yaxes(title_text="Frecuencia (Casos)", secondary_y=False)
fig_pareto.update_yaxes(title_text="Porcentaje Acumulado (%)", secondary_y=True, range=[0, 105])


# =========================================================================
# 5. ALMACENAMIENTO Y DESPLIEGUE EN EL ECOSISTEMA
# =========================================================================
# Exportación directa a HTML para evitar el error de pantalla en negro en tu IDE
print("Exportando componentes visuales del Tablero de Control...")
fig_medicos.write_html("1_dashboard_productividad_individual.html")
fig_geo.write_html("2_dashboard_zonas_criticas.html")
fig_pareto.write_html("3_dashboard_causa_raiz.html")

print("\n¡PROCESO COMPLETADO EXITOSAMENTE!")
print("Se han generado 3 archivos interactivos (.html) en la carpeta de tu script.")
print("Solo debes buscarlos y abrirlos con doble clic desde tu navegador web habitual.")
print("=" * 60)

# Descomenta las siguientes líneas si solucionaste la configuración de tu IDE 
# y prefieres forzar la visualización en vivo en pestañas automáticas:
# fig_medicos.show()
# fig_geo.show()
# fig_pareto.show()