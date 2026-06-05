import os
import numpy as np
import pandas as pd
from weasyprint import HTML

# 1. Crear los datos sintéticos estructurados en DataFrames para la documentación
medicos_data = {
    'ID_Médico': ['MED-001', 'MED-002', 'MED-003', 'MED-004', 'MED-005', 'MED-006'],
    'Nombre del Profesional': ['Dr. Carlos Mendoza', 'Dra. Diana Restrepo', 'Dr. Andrés Felipe Ruiz', 'Dra. Elena Santamaría', 'Dr. Mauricio Gómez', 'Dra. Adriana Lucía'],
    'Programa Clínico': ['Crónicos', 'Paliativos', 'Atención General', 'Crónicos', 'Paliativos', 'Atención General'],
    'Registros Columna D (Agendadas)': [135, 120, 112, 88, 140, 118], 
    'Citas Anuladas / Canceladas': [5, 2, 7, 3, 35, 0]
}
df_medicos = pd.DataFrame(medicos_data)
df_medicos['Consultas Efectivas'] = df_medicos['Registros Columna D (Agendadas)'] - df_medicos['Citas Anuladas / Canceladas']
df_medicos['Tasa Cumplimiento (%)'] = ((df_medicos['Consultas Efectivas'] / 120) * 100).round(1)

def calcular_estado(tasa):
    if tasa >= 90.0: return 'Adecuada'
    elif tasa >= 80.0: return 'En Observación'
    return 'Inadecuada'
df_medicos['Estado Productividad'] = df_medicos['Tasa Cumplimiento (%)'].apply(calcular_estado)

# Formatear tablas para HTML
tabla_medicos_html = df_medicos.to_html(index=False, classes='data-table')

# Datos de Cancelaciones por Localidad y Motivo
geo_data = {
    'Zona / Localidad (Bogotá)': ['Kennedy', 'Suba', 'Bosa', 'Engativá', 'Usaquén', 'Ciudad Bolívar'],
    'Número de Cancelaciones': [63, 42, 35, 20, 8, 7],
    'Porcentaje del Total (%)': [36.0, 24.0, 20.0, 11.4, 4.6, 4.0]
}
df_geo = pd.DataFrame(geo_data)
tabla_geo_html = df_geo.to_html(index=False, classes='data-table')

motivos_data = {
    'Causa / Motivo de Anulación': [
        'Paciente ausente en el domicilio',
        'Hospitalización previa reportada en red hospitalaria',
        'Rechazo directo del servicio por el cuidador',
        'Falla logística de la IPS (Dirección errónea / Cobertura)',
        'Cancelación administrativa / Fuerza mayor fuerza médica'
    ],
    'Casos Mensuales': [79, 44, 26, 18, 8],
    'Porcentaje Acumulado (%)': [45.1, 70.3, 85.1, 95.4, 100.0]
}
df_motivos = pd.DataFrame(motivos_data)
tabla_motivos_html = df_motivos.to_html(index=False, classes='data-table')

# 2. Generar el documento HTML con diseño profesional adaptado para WeasyPrint
html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Estructura de Arquitectura: Tablero de Control de Productividad Médica</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm;
            background-color: #ffffff;
            @bottom-right {{
                content: "Página " counter(page) " de " counter(pages);
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 8pt;
                color: #718096;
            }}
            @bottom-left {{
                content: "Virrey Solís IPS - Documento de Arquitectura Táctica";
                font-family: 'Helvetica Neue', Arial, sans-serif;
                font-size: 8pt;
                color: #718096;
            }}
        }}
        
        *, *::before, *::after {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            color: #2d3748;
            line-height: 1.5;
            margin: 0;
            padding: 0;
            font-size: 10.5pt;
        }}
        
        .header-banner {{
            background-color: #0c4a6e;
            color: #ffffff;
            margin: -20mm -15mm 25px -15mm;
            padding: 30px 15mm;
            border-bottom: 5px solid #0284c7;
        }}
        
        .header-banner h1 {{
            font-size: 20pt;
            margin: 0 0 5px 0;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}
        
        .header-banner p {{
            font-size: 11pt;
            margin: 0;
            color: #e0f2fe;
            font-style: italic;
        }}
        
        h2 {{
            color: #0c4a6e;
            font-size: 14pt;
            margin-top: 25px;
            margin-bottom: 12px;
            padding-left: 10px;
            border-left: 4px solid #0284c7;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #1e293b;
            font-size: 12pt;
            margin-top: 18px;
            margin-bottom: 8px;
            page-break-after: avoid;
        }}
        
        p {{
            margin-top: 0;
            margin-bottom: 12px;
            text-align: justify;
        }}
        
        ul, ol {{
            margin-top: 0;
            margin-bottom: 15px;
            padding-left: 20px;
        }}
        
        li {{
            margin-bottom: 6px;
        }}
        
        .math {{
            font-family: 'Times New Roman', Times, serif;
            font-style: italic;
            font-weight: bold;
            color: #0369a1;
        }}
        
        .equation-box {{
            text-align: center;
            margin: 15px 0;
            font-size: 11.5pt;
            background-color: #f8fafc;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
            margin-bottom: 20px;
            font-size: 9.5pt;
        }}
        
        .data-table th {{
            background-color: #0f172a;
            color: #ffffff;
            font-weight: bold;
            text-align: left;
            padding: 8px 10px;
            border: 1px solid #334155;
        }}
        
        .data-table td {{
            padding: 8px 10px;
            border: 1px solid #cbd5e1;
        }}
        
        .data-table tr:nth-child(even) {{
            background-color: #f8fafc;
        }}
        
        .callout-box {{
            background-color: #f0fdf4;
            border-left: 4px solid #16a34a;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 0 4px 4px 0;
            page-break-inside: avoid;
        }}
        
        .callout-box h4 {{
            margin: 0 0 5px 0;
            color: #14532d;
            font-size: 11pt;
        }}
        
        .callout-box p {{
            margin: 0;
            font-size: 10pt;
            color: #166534;
        }}
        
        .code-block {{
            background-color: #1e293b;
            color: #f8fafc;
            padding: 12px;
            font-family: monospace;
            font-size: 9pt;
            border-radius: 4px;
            margin: 15px 0;
            white-space: pre-wrap;
        }}
        
        .grid-2 {{
            width: 100%;
            display: table;
            table-layout: fixed;
            margin-bottom: 20px;
        }}
        
        .grid-cell {{
            display: table-cell;
            vertical-align: top;
            padding-right: 10px;
        }}
        
        .grid-cell:last-child {{
            padding-right: 0;
            padding-left: 10px;
        }}
    </style>
</head>
<body>

    <div class="header-banner">
        <h1>Especificación de Arquitectura de Datos y Frontend</h1>
        <p>Estructura Integral del Tablero de Control de Productividad Médica — Virrey Solís IPS</p>
    </div>

    <h2>1. Introducción y Propósito del Ecosistema</h2>
    <p>
        El presente documento define la especificación detallada para el diseño, desarrollo e implementación del 
        <strong>Tablero de Control de Productividad Médica</strong> especializado para el servicio de atención domiciliaria 
        (atención en casa) de Virrey Solís IPS. El objetivo primordial de este ecosistema de analítica es optimizar la 
        supervisión y auditoría del talento humano médico, correlacionando de manera directa el volumen registrado de atenciones 
        con las variables de entorno logístico, la distribución urbana de pérdidas de agenda y las causas raíz de inasistencia. 
        Este tablero actuará como el eslabón final del ecosistema informático corporativo, consolidando la información de valor 
        operativo para la alta dirección y los coordinadores de zona.
    </p>

    <h2>2. Requerimientos Tácticos y Parámetros del Sistema</h2>
    <ul>
        <li><strong>Origen de la Información:</strong> Los datos operativos crudos se extraerán directamente de la <strong>Columna D</strong> de la plataforma operativa transaccional de la IPS. Esta columna contiene el histórico unificado de citas agendadas, horas de asignación, bloqueos de agenda y cancelaciones registradas por el personal de call center o los mismos profesionales en campo.</li>
        <li><strong>Frecuencia de Reporte y Segmentación:</strong> El pipeline de datos procesará la información con una <strong>periodicidad mensual</strong> cerrada. El tablero permitirá realizar cortes históricos mes a mes, asegurando una visualización consolidada ideal para los comités de gestión del talento humano.</li>
        <li><strong>Posicionamiento Tecnológico:</strong> La interfaz de usuario e ingesta se ubicará de manera estricta en la <strong>sección final de la arquitectura digital</strong> corporativa. Esto significa que actuará como una capa OLAP de salida, alimentada por los procesos automáticos de extracción del data warehouse sin interferir con la operación transaccional del día a día (OLTP).</li>
    </ul>

    <h2>3. Arquitectura del Pipeline de Datos (Backend)</h2>
    <p>
        Para transformar los registros crudos de la Columna D en variables métricas accionables, el motor de análisis de datos aplicará reglas basadas en la normativa laboral vigente y en el modelo operativo de atención domiciliaria de la institución.
    </p>
    
    <h3>3.1. Reglas de Negocio del Talento Humano</h3>
    <p>
        Tomando como referencia una jornada laboral estándar contratada de <strong>36 horas semanales</strong>, la capacidad operativa mensual de un profesional médico de tiempo completo se proyecta sobre un promedio estable de 4 semanas completas:
    </p>
    <div class="equation-box">
        Capacidad Mensual Base = 36 horas/semana &times; 4 semanas = <span class="math">144 \text{ horas de consulta/mes}</span>
    </div>
    <p>
        Considerando la naturaleza del servicio domiciliario urbano, donde cada valoración médica cuenta con un tiempo estándar de atención de 45 a 60 minutos (que contempla la evaluación clínica in situ, el diligenciamiento de la historia clínica en la plataforma y el desplazamiento geográfico optimizado entre domicilios), se define institucionalmente una <strong>Meta Estándar de 120 Consultas Efectivas al mes</strong> por cada médico equivalente a tiempo completo.
    </p>

    <h3>3.2. Modelado de Fórmulas Analíticas</h3>
    <p>
        El cálculo individual de desempeño descarta las afectaciones externas para medir la eficiencia pura del profesional, evaluando de forma paralela la pérdida operativa general mediante las siguientes ecuaciones:
    </p>
    
    <p><strong>A. Consultas Efectivas Realizadas:</strong></p>
    <div class="equation-box">
        <span class="math">CE = C_{totales} (Columna\ D) - C_{anuladas}</span>
    </div>

    <p><strong>B. Tasa de Cumplimiento de Productividad Individual:</strong></p>
    <div class="equation-box">
        <span class="math">TC = \left( \frac{CE}{\text{Meta Mensual Institucional (120)}} \right) \times 100</span>
    </div>

    <p><strong>C. Tasa de Cancelación Global de Agenda:</strong></p>
    <div class="equation-box">
        <span class="math">T_{cancelación} = \left( \frac{\sum C_{anuladas}}{\sum C_{totales} (Columna\ D)} \right) \times 100</span>
    </div>

    <h2>4. Especificación Completa del Frontend (Interfaz Interactiva)</h2>
    <p>
        El diseño del panel de control interactivo (construido sobre el framework <strong>Streamlit</strong> de Python) se compone de secciones modulares perfectamente delimitadas para guiar al usuario desde los indicadores macro de la IPS hasta las causas específicas de ineficiencia operativa.
    </p>

    <h3>4.1. Capa Superior: KPIs Consolidados del Ecosistema</h3>
    <p>
        Presentación mediante tarjetas de métricas dinámicas que reaccionan de manera inmediata a los filtros de fecha y programa médico:
    </p>
    <ul>
        <li><strong>Consultas Efectivas Totales:</strong> Sumatoria neta de visitas médicas domiciliarias completadas exitosamente en el periodo de corte.</li>
        <li><strong>Promedio de Rendimiento Médico:</strong> Media aritmética de la tasa de cumplimiento de todo el pool de profesionales evaluados.</li>
        <li><strong>Tasa de Cancelación Global:</strong> Porcentaje de citas perdidas que permite prender alertas sobre la planeación logística de rutas.</li>
        <li><strong>Casos de Productividad Inadecuada:</strong> Contador en tiempo real de profesionales que se ubican bajo el umbral mínimo aceptado.</li>
    </ul>

    <h3>4.2. Módulo de Desempeño Individual y Clasificación Semafórica</h3>
    <p>
        Visualización tabular avanzada con formateo de color condicional automatizado para una auditoría de talento humano rápida y eficiente:
    </p>
    <ul>
        <li><strong style="color: #155724;">Adecuada (Verde):</strong> Tasa de Cumplimiento <span class="math">\ge 90.0\%</span> (Mínimo 108 consultas efectivas mensuales). Indica un desempeño sobresaliente u óptimo dentro de su zona operativa asignada.</li>
        <li><strong style="color: #856404;">En Observación (Amarillo):</strong> Tasa de Cumplimiento entre <span class="math">80.0\%</span> y <span class="math">89.9\%</span>. Alerta preventiva relacionada comúnmente con alta dispersión geográfica o congestión en rutas de traslado urbano.</li>
        <li><strong style="color: #721c24;">Inadecuada (Rojo):</strong> Tasa de Cumplimiento <span class="math">&lt; 80.0\%</span> (Menos de 96 consultas efectivas). Disparador inmediato de auditoría interna de la agenda para descartar fallas de registro en la Columna D o problemas severos de cobertura.</li>
    </ul>

    {tabla_medicos_html}

    <div class="callout-box">
        <h4>Nota de Control Institucional</h4>
        <p>Los datos de rendimiento presentados en la tabla superior corresponden al procesamiento simulado del cierre del ecosistema de analítica. El sistema aplica formato condicional estricto sobre la columna "Estado Productividad" para mitigar errores de interpretación visual.</p>
    </div>

    <div style="page-break-before: always;"></div>

    <h3>4.3. Módulo de Pérdidas Logísticas: Distribución Geográfica y Causales</h3>
    <p>
        Para solucionar las fallas operativas de la atención domiciliaria, el tablero desglosa el impacto urbano de las citas perdidas empleando cruces geográficos y ordenamiento estadístico.
    </p>

    <div class="grid-2">
        <div class="grid-cell">
            <h3>Distribución Geográfica por Localidades</h3>
            <p>Segmentación por zonas de la ciudad para identificar focos críticos de inasistencia externa:</p>
            {tabla_geo_html}
        </div>
        <div class="grid-cell">
            <h3>Análisis de Pareto: Motivos de Anulación</h3>
            <p>Clasificación jerárquica de las causas de cancelación para separar responsabilidades operativas:</p>
            {tabla_motivos_html}
        </div>
    </div>

    <h2>5. Requerimientos de Exportación e Interoperabilidad Corporativa</h2>
    <p>
        Para cumplir con los estándares de control interno y auditoría externa de Virrey Solís IPS, el sistema implementará dos flujos nativos de descarga de información directamente integrados en la interfaz de usuario:
    </p>
    <ol>
        <li>
            <strong>Módulo de Descarga a Archivos de Hoja de Cálculo (Excel):</strong> 
            Cada componente gráfico y tabular del tablero contará con un botón de descarga contextualizado (<code>st.download_button</code>). Al ser accionado, la aplicación procesará el DataFrame activo en memoria y generará un archivo binario en formato <code>.xlsx</code> o <code>.csv</code> mediante la librería <code>openpyxl</code>, preservando los encabezados limpios para permitir análisis externos o cruces mediante tablas dinámicas corporativas.
        </li>
        <li>
            <strong>Generación Automatizada de Reportes Ejecutivos en PDF:</strong> 
            El cierre del ecosistema digital contará con un disparador central de generación de reportes corporativos. Al activarse, un pipeline secundario renderizará una plantilla HTML estructurada con los datos consolidados del mes, las tablas de clasificación semafórica de médicos y los resúmenes logísticos geográficos. Utilizando el motor de conversión <code>Weasyprint</code>, el sistema compilará un archivo PDF imprimible y de alta fidelidad visual, cumpliendo con la hoja de estilo institucional de la organización y listo para su distribución a la junta directiva.
        </li>
    </ol>

</body>
</html>
"""

# Guardar HTML intermedio
with open("reporte_intermedio.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Compilar PDF usando WeasyPrint
HTML("reporte_intermedio.html").write_pdf("Estructura_Tablero_Productividad_Medica.pdf")

print("PDF generado con éxito: Estructura_Tablero_Productividad_Medica.pdf")