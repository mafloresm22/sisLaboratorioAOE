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
            # 1. Verificar si ya existe
            check_query = "SELECT idUnidad FROM Unidad WHERE LOWER(nombreUnidad) = LOWER(%s)"
            cursor.execute(check_query, (nombre.strip(),))
            if cursor.fetchone():
                return "exists"

            # 2. Insertar si no existe
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

    @staticmethod
    def update_unidad(id_unidad, nuevo_nombre):
        """Actualiza el nombre de una unidad."""
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Verificar si ya existe otra unidad con ese nombre
            check_query = "SELECT idUnidad FROM Unidad WHERE LOWER(nombreUnidad) = LOWER(%s) AND idUnidad <> %s"
            cursor.execute(check_query, (nuevo_nombre.strip(), id_unidad))
            if cursor.fetchone():
                return "exists"
            
            # 2. Actualizar
            query = "UPDATE Unidad SET nombreUnidad = %s WHERE idUnidad = %s"
            cursor.execute(query, (nuevo_nombre.strip(), id_unidad))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (update_unidad): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def delete_unidad(id_unidad):
        """Elimina una unidad de medida."""
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # Verificar si está en uso
            check_query = "SELECT COUNT(*) FROM Instrumento WHERE unidadId = %s"
            cursor.execute(check_query, (id_unidad,))
            if cursor.fetchone()[0] > 0:
                return "in_use"
            
            # 2. Eliminar
            query = "DELETE FROM Unidad WHERE idUnidad = %s"
            cursor.execute(query, (id_unidad,))
            conn.commit()
            return True
        except Exception as e:
            # Si hay error de llave foránea, devolvemos in_use
            if "foreign key" in str(e).lower():
                return "in_use"
            print(f"🔴 Error SQL (delete_unidad): {e}")
            return False
        finally:
            if conn: conn.close()
