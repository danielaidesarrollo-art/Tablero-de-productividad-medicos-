import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# =========================================================================
# 1. CONFIGURACIÓN ESTÉTICA DEL TABLERO (Estilo limpio)
# =========================================================================
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
# 3. PROCESAMIENTO Y PRODUCCIÓN DE LOS 3 GRÁFICOS
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

plt.figure(figsize=(10, 5))
bars = plt.bar(df_medicos['Columna_T'], df_medicos['Citas_Efectivas'], color=colores_semaforo, edgecolor='black', alpha=0.8)
plt.axhline(y=META_PRODUCCION, color='blue', linestyle='--', linewidth=2, label=f'Meta Institucional ({META_PRODUCCION})')
plt.title('MÓDULO II: Productividad Individual por Médico\n(Verde: Óptimo | Amarillo: Aceptable | Rojo: Bajo Rendimiento)', pad=15)
plt.ylabel('Citas Realizadas Exitosamente')
plt.xlabel('Médico (Columna T)')
plt.xticks(rotation=15, ha='right')
plt.ylim(0, max(df_medicos['Citas_Efectivas']) + 30)

# Añadir etiquetas de porcentaje sobre las barras
for bar, pct in zip(bars, df_medicos['Porcentaje']):
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 3, f'{pct:.1f}%', ha='center', va='bottom', fontweight='bold')

plt.legend(loc='lower right')
plt.tight_layout()
plt.savefig('1_productividad_individual.png', dpi=300) # Guardar como imagen física
plt.close()


# --- GRÁFICO 2: Análisis Geográfico de Anulaciones ---
df_geografico = df_mes[df_mes['Columna_D'].isin(['Cancelada por el Usuario', 'Inasistencia'])].groupby('Localidad').size().reset_index(name='Total_Anulaciones').sort_values(by='Total_Anulaciones', ascending=False)

plt.figure(figsize=(10, 5))
sns.barplot(data=df_geografico, x='Total_Anulaciones', y='Localidad', palette='Reds_r', edgecolor='black')
plt.title('MÓDULO III: Zonas Críticas - Volumen de Inasistencias y Cancelaciones por Localidad', pad=15)
plt.xlabel('Cantidad de Novedades Registradas')
plt.ylabel('Sector / Localidad de Bogotá')
plt.tight_layout()
plt.savefig('2_zonas_criticas_bogota.png', dpi=300) # Guardar como imagen física
plt.close()


# --- GRÁFICO 3: Diagrama de Pareto de Motivos (Columna D) ---
df_motivos = df_mes[df_mes['Motivo_Detallado'] != 'N/A'].groupby('Motivo_Detallado').size().reset_index(name='Cantidad').sort_values(by='Cantidad', ascending=False)
df_motivos['Porcentaje_Acumulado'] = (df_motivos['Cantidad'].cumsum() / df_motivos['Cantidad'].sum()) * 100

fig, ax1 = plt.subplots(figsize=(11, 5))

# Barra principal
ax1.bar(df_motivos['Motivo_Detallado'], df_motivos['Cantidad'], color='#34495e', edgecolor='black', alpha=0.85)
ax1.set_title('MÓDULO IV: Análisis Causa Raíz (Pareto) de Anulación de Consultas', pad=15)
ax1.set_ylabel('Frecuencia (Cantidad de Casos)', color='#34495e')
ax1.set_xlabel('Motivos de Cancelación / Inasistencia (Derivados de Columna D)')
ax1.tick_params(axis='y', labelcolor='#34495e')
plt.xticks(rotation=20, ha='right')

# Línea de porcentaje acumulado
ax2 = ax1.twinx()
ax2.plot(df_motivos['Motivo_Detallado'], df_motivos['Porcentaje_Acumulado'], color='#e67e22', marker='D', linewidth=2, label='% Acumulado')
ax2.set_ylabel('Porcentaje Acumulado (%)', color='#e67e22')
ax2.tick_params(axis='y', labelcolor='#e67e22')
ax2.set_ylim(0, 105)

plt.tight_layout()
plt.savefig('3_analisis_pareto_motivos.png', dpi=300) # Guardar como imagen física
plt.close()


# =========================================================================
# 4. CONFIRMACIÓN FINAL
# =========================================================================
print("=" * 70)
print("¡IMÁGENES DEL TABLERO GENERADAS SIN ERRORES EN TU DISCO DURO!")
print("=" * 70)
print("Busca en la misma carpeta donde tienes guardado este código script:")
print(" -> '1_productividad_individual.png'  (Gráfico del Semáforo Médico)")
print(" -> '2_zonas_criticas_bogota.png'     (Gráfico de Sectores de Bogotá)")
print(" -> '3_analisis_pareto_motivos.png'    (Gráfico de Causas Raíz)")
print("\nPuedes abrirlas directamente como cualquier fotografía. ¡Problema de pantalla resuelto!")
print("=" * 70)