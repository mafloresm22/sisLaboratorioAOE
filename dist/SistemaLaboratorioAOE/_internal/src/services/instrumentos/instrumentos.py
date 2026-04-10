from database.connection import DatabaseConnection
from models.instrumentos.instrumentos import Instrumento
from utils.paths import get_storage_path
import os
import shutil
from datetime import datetime

class InstrumentoService:
    @staticmethod
    def _save_instrumento_image(source_path):
        if not source_path:
            return source_path
        
        relative_folder = os.path.join("storage", "instrumentos")
        storage_dir = get_storage_path(relative_folder)
        
        abs_source = os.path.abspath(source_path)
        if not os.path.isfile(abs_source):
            return source_path

        if os.path.dirname(os.path.abspath(abs_source)) == os.path.abspath(storage_dir):
            filename = os.path.basename(abs_source)
            return os.path.join(relative_folder, filename).replace("\\", "/")
            
        filename = os.path.basename(abs_source)
        base, ext = os.path.splitext(filename)
        base = "".join(x for x in base if x.isalnum() or x in "._- ")[:30].strip().replace(" ", "_")
        unique_name = f"inst_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{base}{ext}"
        dest_path = os.path.join(storage_dir, unique_name)
        
        try:
            os.makedirs(storage_dir, exist_ok=True)
            shutil.copy2(abs_source, dest_path)
            return os.path.join(relative_folder, unique_name).replace("\\", "/")
        except Exception as e:
            print(f"🔴 Error al guardar imagen de instrumento: {e}")
            return source_path

    @staticmethod
    def get_all_instrumentos():
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    i.idInstrumento, 
                    i.descripcionInstrumento, 
                    i.cantidadInstrumento, 
                    i.marcaInstrumento,
                    i.modeloInstrumento, 
                    i.serieInstrumento, 
                    i.colorInstrumento, 
                    i.tamanoInstrumento,
                    i.pisoInstrumento, 
                    i.idEstadoCons, 
                    i.usuarioId, 
                    i.laboratorioId, 
                    i.unidadId,
                    i.imagenInstrumento, 
                    i.estado, 
                    l.nombreLaboratorios,
                    u.nombreUnidad
                FROM Instrumento i
                LEFT JOIN Laboratorios l ON i.laboratorioId = l.idLaboratorios
                LEFT JOIN Unidad u ON i.unidadId = u.idUnidad
                ORDER BY i.idInstrumento ASC
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            
            instrumentos = []
            for fila in filas:
                inst = Instrumento(
                    idInstrumento=fila[0],
                    descripcionInstrumento=fila[1],
                    cantidadInstrumento=fila[2],
                    marcaInstrumento=fila[3],
                    modeloInstrumento=fila[4],
                    serieInstrumento=fila[5],
                    colorInstrumento=fila[6],
                    tamanoInstrumento=fila[7],
                    pisoInstrumento=fila[8],
                    idEstadoCons=fila[9],
                    usuarioId=fila[10],
                    laboratorioId=fila[11],
                    unidadId=fila[12],
                    imagenInstrumento=fila[13],
                    estado=fila[14]
                )

                inst.nombre_laboratorio = fila[15]
                inst.nombre_unidad = fila[16]
                instrumentos.append(inst)
            return instrumentos
        except Exception as e:
            print(f"🔴 Error SQL (get_all_instrumentos): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_instrumento(instrumento: Instrumento):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            
            # Verificar si ya existe (Mismo nombre, marca, modelo, serie, color y tamaño)
            check_query = """
                SELECT idInstrumento FROM Instrumento 
                WHERE descripcionInstrumento IS NOT DISTINCT FROM %s
                  AND marcaInstrumento IS NOT DISTINCT FROM %s
                  AND modeloInstrumento IS NOT DISTINCT FROM %s 
                  AND serieInstrumento IS NOT DISTINCT FROM %s 
                  AND colorInstrumento IS NOT DISTINCT FROM %s 
                  AND tamanoInstrumento IS NOT DISTINCT FROM %s
                LIMIT 1
            """
            cursor.execute(check_query, (
                instrumento.descripcionInstrumento,
                instrumento.marcaInstrumento,
                instrumento.modeloInstrumento,
                instrumento.serieInstrumento,
                instrumento.colorInstrumento,
                instrumento.tamanoInstrumento
            ))
            
            if cursor.fetchone():
                return "exists"

            query = """
                INSERT INTO Instrumento (
                    descripcionInstrumento, cantidadInstrumento, marcaInstrumento, 
                    modeloInstrumento, serieInstrumento, colorInstrumento, 
                    tamanoInstrumento, pisoInstrumento, idEstadoCons, 
                    usuarioId, laboratorioId, unidadId, imagenInstrumento, estado
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Disponible')
                RETURNING idInstrumento
            """
            cursor.execute(query, (
                instrumento.descripcionInstrumento,
                instrumento.cantidadInstrumento,
                instrumento.marcaInstrumento,
                instrumento.modeloInstrumento,
                instrumento.serieInstrumento,
                instrumento.colorInstrumento,
                instrumento.tamanoInstrumento,
                instrumento.pisoInstrumento,
                instrumento.idEstadoCons,
                instrumento.usuarioId,
                instrumento.laboratorioId,
                instrumento.unidadId,
                InstrumentoService._save_instrumento_image(instrumento.imagenInstrumento)
            ))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            print(f"🔴 Error SQL (create_instrumento): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def update_instrumento(instrumento: Instrumento):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = """
                UPDATE Instrumento SET 
                    descripcionInstrumento = %s,
                    cantidadInstrumento = %s,
                    marcaInstrumento = %s,
                    modeloInstrumento = %s,
                    serieInstrumento = %s,
                    colorInstrumento = %s,
                    tamanoInstrumento = %s,
                    pisoInstrumento = %s,
                    idEstadoCons = %s,
                    usuarioId = %s,
                    laboratorioId = %s,
                    unidadId = %s,
                    imagenInstrumento = %s
                WHERE idInstrumento = %s
            """
            cursor.execute(query, (
                instrumento.descripcionInstrumento,
                instrumento.cantidadInstrumento,
                instrumento.marcaInstrumento,
                instrumento.modeloInstrumento,
                instrumento.serieInstrumento,
                instrumento.colorInstrumento,
                instrumento.tamanoInstrumento,
                instrumento.pisoInstrumento,
                instrumento.idEstadoCons,
                instrumento.usuarioId,
                instrumento.laboratorioId,
                instrumento.unidadId,
                InstrumentoService._save_instrumento_image(instrumento.imagenInstrumento),
                instrumento.idInstrumento
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (update_instrumento): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def delete_instrumento(id_instrumento):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT imagenInstrumento FROM Instrumento WHERE idInstrumento = %s", (id_instrumento,))
            fila = cursor.fetchone()
            imagen_path = fila[0] if fila else None
            
            query = "DELETE FROM Instrumento WHERE idInstrumento = %s"
            cursor.execute(query, (id_instrumento,))
            conn.commit()

            if imagen_path and "storage/instrumentos" in imagen_path:
                full_path = get_storage_path(imagen_path)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print(f"⚠️ No se pudo eliminar el archivo físico: {e}")

            return True
        except Exception as e:
            print(f"🔴 Error SQL (delete_instrumento): {e}")
            return False
        finally:
            if conn: conn.close()
