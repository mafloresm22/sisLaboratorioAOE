from database.connection import DatabaseConnection
from models.prestamos.prestamos import Prestamo
import os

class PrestamoService:
    @staticmethod
    def get_all_prestamos():
        """Obtiene la lista de préstamos con información del usuario."""
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.idPrestamo, 
                    p.usuarioId, 
                    p.fechaSolicitud, 
                    p.fechaLimitePrestamo, 
                    p.motivoPrestamo, 
                    p.estadoPrestamo,
                    u.nombreUsuarios
                FROM Prestamo p
                LEFT JOIN Usuarios u ON p.usuarioId = u.idUsuarios
                ORDER BY p.fechaSolicitud DESC
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            
            prestamos = []
            for fila in filas:
                p = Prestamo(
                    idPrestamo=fila[0],
                    usuarioId=fila[1],
                    fechaSolicitud=fila[2],
                    fechaLimitePrestamo=fila[3],
                    motivoPrestamo=fila[4],
                    estadoPrestamo=fila[5]
                )
                p.nombre_usuario = fila[6] # Atributo adicional para la tabla
                prestamos.append(p)
            return prestamos
        except Exception as e:
            print(f"🔴 Error SQL (get_all_prestamos): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_prestamo(prestamo: Prestamo, detalles: list):
        """
        Crea un préstamo y sus detalles en una sola transacción.
        detalles: Lista de diccionarios con {'instrumentoId': id, 'cantidadSolicitada': cant}
        """
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            
            # 1. Insertar Cabecera
            query_p = """
                INSERT INTO Prestamo (usuarioId, fechaLimitePrestamo, motivoPrestamo, estadoPrestamo)
                VALUES (%s, %s, %s, 'activo')
                RETURNING idPrestamo
            """
            cursor.execute(query_p, (prestamo.usuarioId, prestamo.fechaLimitePrestamo, prestamo.motivoPrestamo))
            id_prestamo = cursor.fetchone()[0]

            # 2. Insertar Detalles
            query_d = """
                INSERT INTO DetallePrestamo (prestamoId, instrumentoId, cantidadSolicitada)
                VALUES (%s, %s, %s)
            """
            for det in detalles:
                cursor.execute(query_d, (id_prestamo, det['instrumentoId'], det['cantidadSolicitada']))
            
            conn.commit()
            return id_prestamo
        except Exception as e:
            print(f"🔴 Error SQL (create_prestamo): {e}")
            conn.rollback()
            return False
        finally:
            if conn: conn.close()
