from database.connection import DatabaseConnection
from models import Usuario

class UsuarioService:
    @staticmethod
    def get_all_usuarios():
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    u.idUsuarios, 
                    u.nombreUsuarios, 
                    u.rolId, 
                    r.nombreRol 
                FROM Usuarios u
                LEFT JOIN Rol r ON u.rolId = r.idRol
                ORDER BY u.idUsuarios ASC
            """
            cursor.execute(query)
            return [
                Usuario(idUsuarios=u[0], nombreUsuarios=u[1], rolId=u[2], nombreRol=u[3] or "Sin Rol") 
                for u in cursor.fetchall()
            ]
        except Exception as e:
            print(f"🔴 Error SQL (get_all_usuarios): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_usuario(nombre, password, rol_id):
        from services.auth_service import AuthService
        hashed_pw = AuthService.hash_password(password)
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Verificar si ya existe el nombre de usuario
            check_query = "SELECT idUsuarios FROM Usuarios WHERE LOWER(nombreUsuarios) = LOWER(%s)"
            cursor.execute(check_query, (nombre.strip(),))
            if cursor.fetchone():
                return "exists"

            # 2. Insertar si no existe
            query = """
                INSERT INTO Usuarios (nombreUsuarios, passwordUsuarios, rolId) 
                VALUES (%s, %s, %s) RETURNING idUsuarios
            """
            cursor.execute(query, (nombre.strip(), hashed_pw, rol_id))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            print(f"🔴 Error SQL (create_usuario): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_usuario_statistics():
        conn = DatabaseConnection.get_connection()
        stats = {"total_usuarios": 0, "administradores": 0, "sin_rol": 0}
        if not conn: return stats
        try:
            cursor = conn.cursor()
            # Total Usuarios
            cursor.execute("SELECT COUNT(*) FROM Usuarios")
            stats["total_usuarios"] = cursor.fetchone()[0]
            
            # Administradores
            cursor.execute("SELECT COUNT(*) FROM Usuarios u JOIN Rol r ON u.rolId = r.idRol WHERE r.nombreRol = 'Administrador'")
            stats["administradores"] = cursor.fetchone()[0]
            
            # Usuarios sin rol
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE rolId IS NULL")
            stats["sin_rol"] = cursor.fetchone()[0]
            
            return stats
        except Exception as e:
            print(f"🔴 Error SQL Stats (Usuarios): {e}")
            return stats
        finally:
            if conn: conn.close()

    @staticmethod
    def update_usuario(id_usuario, nuevo_nombre, nuevo_rol_id):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            # 1. Verificar si el nombre ya existe en otro usuario
            check_query = "SELECT idUsuarios FROM Usuarios WHERE LOWER(nombreUsuarios) = LOWER(%s) AND idUsuarios != %s"
            cursor.execute(check_query, (nuevo_nombre.strip(), id_usuario))
            if cursor.fetchone():
                return "exists"

            # 2. Actualizar
            query = "UPDATE Usuarios SET nombreUsuarios = %s, rolId = %s WHERE idUsuarios = %s"
            cursor.execute(query, (nuevo_nombre.strip(), nuevo_rol_id, id_usuario))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (update_usuario): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def reset_password(id_usuario, nuevo_password="123456"):
        from services.auth_service import AuthService
        hashed_pw = AuthService.hash_password(nuevo_password)
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = "UPDATE Usuarios SET passwordUsuarios = %s WHERE idUsuarios = %s"
            cursor.execute(query, (hashed_pw, id_usuario))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (reset_password): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def delete_usuario(id_usuario):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            query = "DELETE FROM Usuarios WHERE idUsuarios = %s"
            cursor.execute(query, (id_usuario,))
            conn.commit()
            return True
        except Exception as e:
            # Si hay error de llave foránea (e.g. tiene préstamos o bitácora)
            if "foreign key constraint" in str(e).lower():
                return "has_dependencies"
            print(f"🔴 Error SQL (delete_usuario): {e}")
            return False
        finally:
            if conn: conn.close()