from database.connection import DatabaseConnection

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
                {"idUsuarios": u[0], "nombreUsuarios": u[1], "rolId": u[2], "nombreRol": u[3] or "Sin Rol"} 
                for u in cursor.fetchall()
            ]
        except Exception as e:
            print(f"🔴 Error SQL (get_all_usuarios): {e}")
            return []
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
            
            # Administradores (Asumiendo que el rol con id 1 o nombre 'Administrador' es el admin)
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
