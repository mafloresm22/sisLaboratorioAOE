import pandas as pd
from tkinter import filedialog
from database.connection import DatabaseConnection

class ExcelImporter:
    @staticmethod
    def importar_instrumentos():
        """
        Abre un cuadro de diálogo para seleccionar un archivo Excel e inserta 
        los datos en la tabla Instrumento omitiendo la columna 'Responsable'.
        """
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        
        if not file_path:
            return False, "Operación cancelada. No se seleccionó ningún archivo."
            
        try:
            # Leer el Excel (Asegurando explícitamente que SOLO lea la primera hoja)
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Limpiar nombres de columnas para que coincidan sin importar espacios
            df.columns = df.columns.str.strip().str.upper()
            
            conn = DatabaseConnection.get_connection()
            if not conn:
                return False, "Error al conectar con la base de datos."
                
            cursor = conn.cursor()
            inserciones = 0
            
            # Iterar sobre las filas del Excel
            for index, row in df.iterrows():
                # 'DESCRIPCIÓN' -> descripcionInstrumento
                descripcion = str(row.get('DESCRIPCIÓN', '')).strip()
                if not descripcion or descripcion.lower() == 'nan':
                    continue # Omitir filas sin descripción
                    
                # 'CANTIDAD' -> cantidadInstrumento
                cantidad = row.get('CANTIDAD', 0)
                try: 
                    cantidad = int(cantidad) if pd.notna(cantidad) else 0
                except: 
                    cantidad = 0
                
                # Helper para strings
                def get_str_val(col_name):
                    val = str(row.get(col_name, '')).strip()
                    return val if val.lower() != 'nan' and val != '' else None
                
                marca = get_str_val('MARCA')
                modelo = get_str_val('MODELO')
                serie = get_str_val('SERIE')
                color = get_str_val('COLOR')
                tamano = get_str_val('TAMAÑO')
                piso = get_str_val('PISO')
                
                # 'ESTADO DE CONSERVACIÓN' -> idEstadoCons
                estado_cons_raw = str(row.get('ESTADO DE CONSERVACIÓN', '')).strip().lower()
                id_estado_cons = 4 # Bueno por defecto
                if 'nuevo' in estado_cons_raw or estado_cons_raw == '5.0' or estado_cons_raw == '5': 
                    id_estado_cons = 5
                elif 'bueno' in estado_cons_raw or estado_cons_raw == '4.0' or estado_cons_raw == '4': 
                    id_estado_cons = 4
                elif 'regular' in estado_cons_raw or estado_cons_raw == '3.0' or estado_cons_raw == '3': 
                    id_estado_cons = 3
                elif 'malo' in estado_cons_raw or estado_cons_raw == '2.0' or estado_cons_raw == '2': 
                    id_estado_cons = 2
                
                # 'UBICACIÓN DEL BIEN' -> laboratorioId (Buscamos por nombre)
                ubicacion = get_str_val('UBICACIÓN DEL BIEN')
                laboratorio_id = None
                if ubicacion:
                    cursor.execute("SELECT idLaboratorios FROM Laboratorios WHERE nombreLaboratorios ILIKE %s LIMIT 1", (f"%{ubicacion}%",))
                    lab_result = cursor.fetchone()
                    if lab_result:
                        laboratorio_id = lab_result[0]
                
                # Valores por defecto para campos no proporcionados
                if not laboratorio_id:
                    laboratorio_id = 1 # Laboratorio por defecto
                
                usuario_id = 1 # Usuario por defecto
                unidad_id = 1 # Unidad por defecto
                imagen_instrumento = None # Guardar en Null en la BD

                # Query para insertar en la tabla Instrumento
                query = """
                    INSERT INTO Instrumento (
                        descripcionInstrumento, cantidadInstrumento, marcaInstrumento, 
                        modeloInstrumento, serieInstrumento, colorInstrumento, 
                        tamanoInstrumento, pisoInstrumento, idEstadoCons, laboratorioId, 
                        usuarioId, unidadId, imagenInstrumento, estado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Disponible')
                """
                
                cursor.execute(query, (
                    descripcion, cantidad, marca, modelo, serie, color, 
                    tamano, piso, id_estado_cons, laboratorio_id,
                    usuario_id, unidad_id, imagen_instrumento
                ))
                inserciones += 1
                
            conn.commit()
            cursor.close()
            conn.close()
            
            return True, f"¡Éxito! Se importaron {inserciones} instrumentos a la base de datos."
            
        except Exception as e:
            # Capturar errores (por ejemplo, si falta pandas o openpyxl o si el formato no es válido)
            return False, f"Error al procesar el Excel:\n{str(e)}"
