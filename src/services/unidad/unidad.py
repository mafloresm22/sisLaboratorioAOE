from database.connection import DatabaseConnection

class UnidadService:
    @staticmethod
    def get_all_unidades():
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    idUnidad, 
                    nombreUnidad 
                FROM Unidad 
                ORDER BY idUnidad ASC
            """
            cursor.execute(query)
            return [{"idUnidad": u[0], "nombreUnidad": u[1]} for u in cursor.fetchall()]
        except Exception as e:
            print(f"🔴 Error SQL (get_all_unidades): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_unidad(nombre):
        """Crea una nueva unidad."""
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = "INSERT INTO Unidad (nombreUnidad) VALUES (%s) RETURNING idUnidad"
            cursor.execute(query, (nombre.strip(),))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            print(f"🔴 Error SQL (create_unidad): {e}")
            return False
        finally:
            if conn: conn.close()
