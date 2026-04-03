from database.connection import DatabaseConnection
from models.laboratorios.laboratorios import Laboratorio

class LaboratorioService:
    @staticmethod
    def get_all_laboratorios():
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Basado en el esquema real: Tabla 'Instrumento', FK 'laboratorioId'
            query = """
                SELECT 
                    L.idLaboratorios, 
                    L.nombreLaboratorios, 
                    L.estadoLaboratorios,
                    COUNT(I.idInstrumento) as total_instrumentos
                FROM Laboratorios L
                LEFT JOIN Instrumento I ON L.idLaboratorios = I.laboratorioId
                GROUP BY L.idLaboratorios, L.nombreLaboratorios, L.estadoLaboratorios
                ORDER BY L.idLaboratorios ASC
            """
            cursor.execute(query)
            return [Laboratorio(idLaboratorios=l[0], nombreLaboratorios=l[1], estadoLaboratorios=l[2], instrument_count=l[3]) for l in cursor.fetchall()]
        except Exception as e:
            # Si la relación Instrumento no existe, devolvemos sin el conteo
            if "no existe la relación" in str(e).lower():
                try:
                    cursor.execute("SELECT idLaboratorios, nombreLaboratorios, estadoLaboratorios FROM Laboratorios ORDER BY idLaboratorios ASC")
                    return [Laboratorio(idLaboratorios=l[0], nombreLaboratorios=l[1], estadoLaboratorios=l[2], instrument_count=0) for l in cursor.fetchall()]
                except:
                    return []
            print(f"🔴 Error SQL (get_all_laboratorios): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_laboratorio(nombre):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            check_query = "SELECT idLaboratorios FROM Laboratorios WHERE LOWER(nombreLaboratorios) = LOWER(%s)"
            cursor.execute(check_query, (nombre.strip(),))
            if cursor.fetchone():
                return "exists"

            query = "INSERT INTO Laboratorios (nombreLaboratorios) VALUES (%s) RETURNING idLaboratorios"
            cursor.execute(query, (nombre.strip(),))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            print(f"🔴 Error SQL (create_laboratorio): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def update_laboratorio(id_laboratorio, nuevo_nombre):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            check_query = "SELECT idLaboratorios FROM Laboratorios WHERE LOWER(nombreLaboratorios) = LOWER(%s) AND idLaboratorios <> %s"
            cursor.execute(check_query, (nuevo_nombre.strip(), id_laboratorio))
            if cursor.fetchone():
                return "exists"
            
            query = "UPDATE Laboratorios SET nombreLaboratorios = %s WHERE idLaboratorios = %s"
            cursor.execute(query, (nuevo_nombre.strip(), id_laboratorio))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (update_laboratorio): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def delete_laboratorio(id_laboratorio):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Laboratorios WHERE idLaboratorios = %s"
            cursor.execute(query, (id_laboratorio,))
            conn.commit()
            return True
        except Exception as e:
            if "foreign key" in str(e).lower():
                return "in_use"
            print(f"🔴 Error SQL (delete_laboratorio): {e}")
            return False
        finally:
            if conn: conn.close()
