# src/services/auth_service.py
import bcrypt
from database.connection import DatabaseConnection

class AuthService:
    @staticmethod
    def hash_password(password):
        """Genera un hash seguro para una contraseña."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verificar_credenciales(nombre_usuario, password_ingresado):
        """Busca al usuario y verifica el hash de la contraseña."""
        conn = DatabaseConnection.get_connection()
        if not conn: return None
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    u.idUsuarios, 
                    u.nombreUsuarios, 
                    u.passwordUsuarios, 
                    u.rolId, 
                    r.nombreRol 
                FROM Usuarios u
                JOIN Rol r ON u.rolId = r.idRol
                WHERE u.nombreUsuarios = %s
            """
            cursor.execute(query, (nombre_usuario,))
            usuario = cursor.fetchone()
            
            if usuario:
                id_user, nombre, hash_almacenado, rol_id, nombre_rol = usuario
                
                # bcrypt necesita los datos en formato bytes para comparar
                if bcrypt.checkpw(password_ingresado.encode('utf-8'), hash_almacenado.encode('utf-8')):
                    return {
                        "idUsuarios": id_user, 
                        "nombreUsuarios": nombre, 
                        "rolId": rol_id, 
                        "nombreRol": nombre_rol
                    }
            
            return None
        except Exception as e:
            print(f"🔴 Error en Login: {e}")
            return None
        finally:
            conn.close()
