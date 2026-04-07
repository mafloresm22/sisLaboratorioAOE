import pandas as pd
import unicodedata
from tkinter import filedialog
from database.connection import DatabaseConnection

class ExcelImporter:
    @staticmethod
    def importar_instrumentos():
        """
        Abre un cuadro de diálogo para seleccionar un archivo Excel e inserta 
        los datos de TODAS las hojas en la tabla Instrumento.
        """
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return False, "Operación cancelada. No se seleccionó ningún archivo."
            
        try:
            # Leer todas las hojas del Excel
            excel_dict = pd.read_excel(file_path, sheet_name=None)
            
            conn = DatabaseConnection.get_connection()
            if not conn:
                return False, "Error al conectar con la base de datos."
                
            cursor = conn.cursor()
            inserciones_totales = 0
            hojas_procesadas = 0
            
            def normalize_text(text):
                if pd.isna(text): return ""
                t = str(text).strip().upper()
                return "".join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')

            # Recorrer cada hoja del libro de Excel
            for sheet_name, df in excel_dict.items():
                if df.empty:
                    continue

                # Normalizar los nombres actuales de las columnas
                df.columns = [normalize_text(c) for c in df.columns]

                # --- DETECCIÓN INTELIGENTE DE CABECERA ---
                # Si la columna DESCRIPCION no está en los encabezados, la buscamos en las primeras 10 filas
                if 'DESCRIPCION' not in df.columns:
                    header_found = False
                    for i in range(min(len(df), 10)):
                        row_normalized = [normalize_text(v) for v in df.iloc[i].values]
                        if 'DESCRIPCION' in row_normalized:
                            df.columns = row_normalized
                            df = df.iloc[i+1:].reset_index(drop=True)
                            header_found = True
                            break
                    if not header_found:
                        continue # Saltar hoja si no hay cabecera válida

                hojas_procesadas += 1

                # Mapeo de columnas basado exactamente en la imagen proporcionada
                def find_col(possible_names):
                    for name in possible_names:
                        norm_name = normalize_text(name)
                        if norm_name in df.columns:
                            return norm_name
                    return None

                col_desc    = find_col(['DESCRIPCIÓN', 'DESCRIPCION'])
                col_cant    = find_col(['CANTIDAD', 'CANT.']) or 'CANTIDAD'
                col_marca   = find_col(['MARCA']) or 'MARCA'
                col_modelo  = find_col(['MODELO']) or 'MODELO'
                col_serie   = find_col(['SERIE']) or 'SERIE'
                col_color   = find_col(['COLOR']) or 'COLOR'
                col_tamano  = find_col(['TAMAÑO', 'TAMANO']) or 'TAMAÑO'
                col_estado  = find_col(['ESTADO DE CONSERVACIÓN', 'ESTADO', 'CONSERVACION']) or 'ESTADO DE CONSERVACIÓN'
                col_ubica   = find_col(['UBICACIÓN DEL BIEN', 'UBICACION', 'UBICACION DEL BIEN', 'LABORATORIO']) or 'UBICACIÓN DEL BIEN'
                col_piso    = find_col(['PISO']) or 'PISO'

                # Iterar sobre las filas de la hoja actual
                for index, row in df.iterrows():
                    descripcion = str(row.get(col_desc, '')).strip()
                    if not descripcion or descripcion.lower() == 'nan' or descripcion == '':
                        continue
                    
                    # CANTIDAD
                    cantidad_raw = row.get(col_cant, 0)
                    try: 
                        cantidad = int(float(cantidad_raw)) if pd.notna(cantidad_raw) else 0
                    except: 
                        cantidad = 0
                    
                    def get_exact_val(col_name):
                        val = row.get(col_name)
                        if pd.isna(val): return None
                        s_val = str(val).strip()
                        return s_val if s_val.lower() != 'nan' and s_val != '' else None
                    
                    marca  = get_exact_val(col_marca)
                    modelo = get_exact_val(col_modelo)
                    serie  = get_exact_val(col_serie)
                    color  = get_exact_val(col_color)
                    tamano = get_exact_val(col_tamano)
                    piso   = get_exact_val(col_piso)
                    
                    # ESTADO DE CONSERVACIÓN
                    estado_cons_raw = str(row.get(col_estado, '')).strip().lower()
                    id_estado_cons = 4
                    if any(x in estado_cons_raw for x in ['nuevo', '5.0', '5', 'excl']): id_estado_cons = 5
                    elif any(x in estado_cons_raw for x in ['bueno', '4.0', '4']): id_estado_cons = 4
                    elif any(x in estado_cons_raw for x in ['regul', '3.0', '3']): id_estado_cons = 3
                    elif any(x in estado_cons_raw for x in ['malo', '2.0', '2', 'deter']): id_estado_cons = 2
                    
                    # UBICACIÓN -> Búsqueda de laboratorio
                    ubicacion = get_exact_val(col_ubica)
                    laboratorio_id = 1
                    
                    if ubicacion:
                        cursor.execute("""
                            SELECT idLaboratorios FROM Laboratorios 
                            WHERE nombreLaboratorios ILIKE %s OR %s ILIKE CONCAT('%%', nombreLaboratorios, '%%')
                            LIMIT 1
                        """, (f"%{ubicacion}%", ubicacion))
                        lab_result = cursor.fetchone()
                        if lab_result:
                            laboratorio_id = lab_result[0]
                    
                    # Inserción
                    cursor.execute("""
                        INSERT INTO Instrumento (
                            descripcionInstrumento, cantidadInstrumento, marcaInstrumento, 
                            modeloInstrumento, serieInstrumento, colorInstrumento, 
                            tamanoInstrumento, pisoInstrumento, idEstadoCons, laboratorioId, 
                            usuarioId, unidadId, estado
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 1, 'Disponible')
                    """, (descripcion, cantidad, marca, modelo, serie, color, tamano, piso, id_estado_cons, laboratorio_id))
                    
                    inserciones_totales += 1
                
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, f"¡Éxito! Se procesaron {hojas_procesadas} hojas y se registraron {inserciones_totales} instrumentos en total."
            
        except Exception as e:
            return False, f"Error crítico al procesar el libro Excel:\n{str(e)}"
