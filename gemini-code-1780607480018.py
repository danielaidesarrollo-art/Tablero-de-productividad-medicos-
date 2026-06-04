# 2. Procesamiento y Limpieza
@st.cache_data
def cargar_y_procesar_datos(archivo_subido):
    df = pd.read_excel(archivo_subido)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    
    archivo_subido.seek(0)
    wb = openpyxl.load_workbook(archivo_subido, data_only=True)
    hoja = wb.active
    
    estados = []
    filas_validas = []
    max_filas = len(df) + 1
    
    for idx, row in enumerate(hoja.iter_rows(min_row=2, max_row=max_filas, max_col=hoja.max_column)):
        color_primera_celda = obtener_color_hex(row[0])
        if es_color_azul(color_primera_celda):
            filas_validas.append(False)
            estados.append("Ignorar")
            continue
            
        filas_validas.append(True)
        cell_f = row[5] if len(row) > 5 else None 
        color_f = obtener_color_hex(cell_f)
        
        f_es_cafe = es_color_cafe(color_f)
        total_cafe_fila = sum(1 for cell in row if es_color_cafe(obtener_color_hex(cell)))
        
        if f_es_cafe:
            if total_cafe_fila > 3: 
                estados.append("Cancelada (Por el paciente)")
            else:
                estados.append("Cancelada (Médico no alcanzó)")
        else:
            estados.append("Consulta Efectiva")
            
    if len(estados) > len(df): estados = estados[:len(df)]
    elif len(estados) < len(df): estados.extend(["Consulta Efectiva"] * (len(df) - len(estados)))
    
    if len(filas_validas) > len(df): filas_validas = filas_validas[:len(df)]
    elif len(filas_validas) < len(df): filas_validas.extend([True] * (len(df) - len(filas_validas)))
            
    df['ESTADO_VISITA'] = estados
    df['ES_VALIDA'] = filas_validas
    df = df[df['ES_VALIDA'] == True].copy()
    
    # Limpieza de textos
    columnas_texto = df.select_dtypes(include=['object']).columns
    for col in columnas_texto:
        df[col] = df[col].astype(str).str.strip().str.upper()
        df[col] = df[col].replace({'NAN': None, 'NONE': None, '': None, 'NAT': None})
        
    # --- FILTROS DE CORRECCIÓN ---
    col_medico = 'MEDICO' if 'MEDICO' in df.columns else df.columns[0]
    
    if col_medico in df.columns:
        # Eliminar filas donde el médico sea nulo
        df.dropna(subset=[col_medico], inplace=True)
        # Eliminar falsos médicos (notas, horas, reservas)
        df = df[~df[col_medico].str.contains(r'AM|PM|RESERVA|MEDICO|PROGRAMAR|ALMUERZO', na=False, regex=True)]
        # Aplicar correcciones ortográficas
        df[col_medico] = df[col_medico].replace(CORRECCIONES_MEDICOS)
        
    # Eliminar turnos en blanco (donde no hay paciente)
    # Intenta detectar la columna del paciente automáticamente
    col_paciente = next((c for c in df.columns if 'PACIENTE' in c or 'NOMBRE' in c or 'DOC' in c or 'CEDULA' in c), None)
    if col_paciente:
        df.dropna(subset=[col_paciente], inplace=True)
        
    # Calcular productividad solo sobre lo que quedó
    df['PRODUCTIVIDAD'] = df['ESTADO_VISITA'].apply(lambda x: 1 if x == "Consulta Efectiva" else 0)
        
    return df