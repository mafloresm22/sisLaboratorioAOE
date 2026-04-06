from database.connection import DatabaseConnection
from models.instrumentos.instrumentos import Instrumento

class InstrumentoService:
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
                    l.nombreLaboratorios
                FROM Instrumento i
                LEFT JOIN Laboratorios l ON i.laboratorioId = l.idLaboratorios
                ORDER BY i.idInstrumento DESC
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
                # Atributo extra para la UI
                inst.nombre_laboratorio = fila[15]
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
            
            # Verificar si ya existe
            check_query = """
                SELECT idInstrumento FROM Instrumento 
                WHERE modeloInstrumento IS NOT DISTINCT FROM %s 
                  AND serieInstrumento IS NOT DISTINCT FROM %s 
                  AND colorInstrumento IS NOT DISTINCT FROM %s 
                  AND tamanoInstrumento IS NOT DISTINCT FROM %s
                LIMIT 1
            """
            cursor.execute(check_query, (
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
                instrumento.imagenInstrumento
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
                instrumento.imagenInstrumento,
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
            query = "DELETE FROM Instrumento WHERE idInstrumento = %s"
            cursor.execute(query, (id_instrumento,))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (delete_instrumento): {e}")
            return False
        finally:
            if conn: conn.close()
