from database.connection import DatabaseConnection
from models.prestamos.prestamos import Prestamo
import os

class PrestamoService:
    @staticmethod
    def get_all_prestamos():
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
                    u.nombreUsuarios,
                    COALESCE((SELECT SUM(cantidadSolicitada) FROM DetallePrestamo WHERE prestamoId = p.idPrestamo), 0) AS cantidadTotal
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
                p.nombre_usuario = fila[6]
                p.cantidad_solicitada = fila[7]
                prestamos.append(p)
            return prestamos
        except Exception as e:
            print(f"🔴 Error SQL (get_all_prestamos): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_prestamo(prestamo: Prestamo, detalles: list):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            
            query_p = """
                INSERT INTO Prestamo (usuarioId, fechaLimitePrestamo, motivoPrestamo, estadoPrestamo)
                VALUES (%s, %s, %s, 'activo')
                RETURNING idPrestamo
            """
            cursor.execute(query_p, (prestamo.usuarioId, prestamo.fechaLimitePrestamo, prestamo.motivoPrestamo))
            id_prestamo = cursor.fetchone()[0]

            # 2. Insertar Detalles y REDUCIR STOCK
            query_d = """
                INSERT INTO DetallePrestamo (
                    prestamoId, instrumentoId, cantidadSolicitada, estadoEntrega
                )
                VALUES (%s, %s, %s, 'ENTREGADO')
            """
            query_update_stock = """
                UPDATE Instrumento 
                SET cantidadInstrumento = cantidadInstrumento - %s 
                WHERE idInstrumento = %s
            """
            for det in detalles:
                # Insertar detalle
                cursor.execute(query_d, (id_prestamo, det['instrumentoId'], det['cantidadSolicitada']))
                # Reducir stock real
                cursor.execute(query_update_stock, (det['cantidadSolicitada'], det['instrumentoId']))
            
            conn.commit()
            return id_prestamo
        except Exception as e:
            print(f"🔴 Error SQL (create_prestamo): {e}")
            conn.rollback()
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def return_prestamo(id_prestamo):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            
            # 1. Obtener los detalles para saber qué instrumentos devolver y cuánto stock sumar
            cursor.execute("SELECT instrumentoId, cantidadSolicitada FROM DetallePrestamo WHERE prestamoId = %s", (id_prestamo,))
            detalles = cursor.fetchall()
            
            # 2. Devolver Stock a cada instrumento
            query_stock = "UPDATE Instrumento SET cantidadInstrumento = cantidadInstrumento + %s WHERE idInstrumento = %s"
            for det in detalles:
                cursor.execute(query_stock, (det[1], det[0]))
            
            # 3. Actualizar fechas y estados en Detalle
            cursor.execute("""
                UPDATE DetallePrestamo 
                SET fechaDevolucion = CURRENT_TIMESTAMP, estadoDevolucion = 'DEVUELTO' 
                WHERE prestamoId = %s
            """, (id_prestamo,))
            
            # 4. Finalizar el Préstamo principal
            cursor.execute("UPDATE Prestamo SET estadoPrestamo = 'devuelto' WHERE idPrestamo = %s", (id_prestamo,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (return_prestamo): {e}")
            conn.rollback()
            return False
        finally:
            if conn: conn.close()
