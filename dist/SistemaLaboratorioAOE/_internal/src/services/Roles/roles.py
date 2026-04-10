from database.connection import DatabaseConnection
from models import Role

class RoleService:
    @staticmethod
    def get_all_roles():
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT R.idRol, R.nombreRol, COUNT(U.idUsuarios) as user_count 
                FROM Rol R 
                LEFT JOIN Usuarios U ON R.idRol = U.rolId 
                GROUP BY R.idRol, R.nombreRol
                ORDER BY R.idRol ASC
            """
            cursor.execute(query)
            return [Role(idRol=r[0], nombreRol=r[1], users=r[2]) for r in cursor.fetchall()]
        except Exception as e:
            print(f"🔴 Error SQL: {e}")
            return []
        finally: conn.close()

    @staticmethod
    def create_role(nombre):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Verificar si ya existe
            check_query = "SELECT idRol FROM Rol WHERE LOWER(nombreRol) = LOWER(%s)"
            cursor.execute(check_query, (nombre.strip(),))
            if cursor.fetchone():
                return "exists"
                
            # 2. Insertar si no existe
            query = "INSERT INTO Rol (nombreRol) VALUES (%s) RETURNING idRol"
            cursor.execute(query, (nombre.strip(),))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            print(f"🔴 Error SQL: {e}")
            return False
        finally: conn.close()

    @staticmethod
    def get_role_statistics():
        conn = DatabaseConnection.get_connection()
        stats = {"total_roles": 0, "active_permissions_count": 0, "users_without_role": 0}
        if not conn: return stats
        try:
            cursor = conn.cursor()
            # Total Roles
            cursor.execute("SELECT COUNT(*) FROM Rol")
            stats["total_roles"] = cursor.fetchone()[0]
            # Usuarios sin rol
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE rolId IS NULL")
            stats["users_without_role"] = cursor.fetchone()[0]
            return stats
        except Exception as e:
            print(f"🔴 Error SQL Stats: {e}")
            return stats
        finally: conn.close()
        
    @staticmethod
    def update_role(id_rol, nuevo_nombre):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Verificar si ya existe otro rol con ese nombre (ignorar el actual)
            check_query = "SELECT idRol FROM Rol WHERE LOWER(nombreRol) = LOWER(%s) AND idRol <> %s"
            cursor.execute(check_query, (nuevo_nombre.strip(), id_rol))
            if cursor.fetchone():
                return "exists"
            
            # 2. Actualizar
            query = "UPDATE Rol SET nombreRol = %s WHERE idRol = %s"
            cursor.execute(query, (nuevo_nombre.strip(), id_rol))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL Update: {e}")
            return False
        finally: conn.close()

    @staticmethod
    def delete_role(id_rol):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Verificar si tiene usuarios asociados para evitar errores de FK
            check_query = "SELECT COUNT(*) FROM Usuarios WHERE rolId = %s"
            cursor.execute(check_query, (id_rol,))
            if cursor.fetchone()[0] > 0:
                return "has_users"
            
            # 2. Eliminar
            query = "DELETE FROM Rol WHERE idRol = %s"
            cursor.execute(query, (id_rol,))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL Delete: {e}")
            return False
        finally: conn.close()
