from database.connection import DatabaseConnection

class ReporteService:
    @staticmethod
    def get_resumen_general():
        conn = DatabaseConnection.get_connection()
        if not conn: return {}
        try:
            cursor = conn.cursor()
            
            # Conteos rápidos
            cursor.execute("SELECT COUNT(*) FROM Instrumento")
            total_instrumentos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Usuarios")
            total_usuarios = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Laboratorios")
            total_laboratorios = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM Prestamo WHERE estadoPrestamo = 'activo'")
            prestamos_activos = cursor.fetchone()[0]

            return {
                "instrumentos": total_instrumentos,
                "usuarios": total_usuarios,
                "laboratorios": total_laboratorios,
                "prestamos_activos": prestamos_activos
            }
        except Exception as e:
            print(f"🔴 Error en get_resumen_general: {e}")
            return {}
        finally:
            conn.close()

    @staticmethod
    def get_instrumentos_por_laboratorio():
        """Retorna la cantidad de instrumentos agrupados por cada laboratorio."""
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT l.nombreLaboratorios, SUM(i.cantidadInstrumento)
                FROM Instrumento i
                JOIN Laboratorios l ON i.laboratorioId = l.idLaboratorios
                GROUP BY l.nombreLaboratorios
                ORDER BY SUM(i.cantidadInstrumento) DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"🔴 Error en get_instrumentos_por_laboratorio: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_estado_conservacion_stats():
        """Retorna la cantidad de instrumentos según su estado de conservación."""
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT ec.nombreEstado, COUNT(*)
                FROM Instrumento i
                JOIN EstadoConservacion ec ON i.idEstadoCons = ec.idEstadoCons
                GROUP BY ec.nombreEstado
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"🔴 Error en get_estado_conservacion_stats: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_prestamos_por_estado():
        """Estadísticas de préstamos (Pendientes, Activos, Devueltos, Atrasados)."""
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT estadoPrestamo, COUNT(*)
                FROM Prestamo
                GROUP BY estadoPrestamo
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"🔴 Error en get_prestamos_por_estado: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_instrumentos_mas_prestados(limit=5):
        """Ranking de instrumentos más solicitados en préstamos."""
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT i.descripcionInstrumento, COUNT(dp.idDetalle) as total_veces
                FROM DetallePrestamo dp
                JOIN Instrumento i ON dp.instrumentoId = i.idInstrumento
                GROUP BY i.idInstrumento, i.descripcionInstrumento
                ORDER BY total_veces DESC
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        except Exception as e:
            print(f"🔴 Error en get_instrumentos_mas_prestados: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_proximas_devoluciones():
        """Lista de préstamos cuya fecha límite está por vencer o vencida."""
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT p.idPrestamo, u.nombreUsuarios, p.fechaLimitePrestamo, p.estadoPrestamo
                FROM Prestamo p
                JOIN Usuarios u ON p.usuarioId = u.idUsuarios
                WHERE p.estadoPrestamo IN ('activo', 'atrasado')
                ORDER BY p.fechaLimitePrestamo ASC
                LIMIT 10
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"🔴 Error en get_proximas_devoluciones: {e}")
            return []
        finally:
            conn.close()
    @staticmethod
    def get_instrumentos_detallados_por_estado():
        """Retorna la lista de instrumentos agrupados por su nombre de estado."""
        conn = DatabaseConnection.get_connection()
        if not conn: return {}
        try:
            cursor = conn.cursor()
            query = """
                SELECT ec.nombreEstado, i.descripcionInstrumento, i.marcaInstrumento, i.modeloInstrumento
                FROM Instrumento i
                JOIN EstadoConservacion ec ON i.idEstadoCons = ec.idEstadoCons
                ORDER BY ec.nombreEstado, i.descripcionInstrumento
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Agrupar en un diccionario por estado
            from collections import defaultdict
            grouped = defaultdict(list)
            for row in rows:
                grouped[row[0]].append({
                    "nombre": row[1],
                    "marca": row[2] or "S/M",
                    "modelo": row[3] or "S/M"
                })
            return dict(grouped)
        except Exception as e:
            print(f"🔴 Error en get_instrumentos_detallados_por_estado: {e}")
            return {}
        finally:
            conn.close()
