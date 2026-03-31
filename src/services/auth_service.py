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
            query = "SELECT idUsuarios, nombreUsuarios, passwordUsuarios, rolId FROM Usuarios WHERE nombreUsuarios = %s"
            cursor.execute(query, (nombre_usuario,))
            usuario = cursor.fetchone()
            
            if usuario:
                id_user, nombre, hash_almacenado, rol = usuario
                
                # bcrypt necesita los datos en formato bytes para comparar
                if bcrypt.checkpw(password_ingresado.encode('utf-8'), hash_almacenado.encode('utf-8')):
                    return {"id": id_user, "nombre": nombre, "rol": rol}
            
            return None
        except Exception as e:
            print(f"🔴 Error en Login: {e}")
            return None
        finally:
            conn.close()
