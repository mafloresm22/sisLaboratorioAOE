from database.connection import DatabaseConnection
from models.laboratorios.laboratorios import Laboratorio

class LaboratorioService:
    @staticmethod
    def get_all_laboratorios():
        conn = DatabaseConnection.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    L.idlaboratorios, 
                    L.nombrelaboratorios, 
                    L."pisoLaboratorios",
                    L.estadolaboratorios,
                    COUNT(I.idinstrumento) as total_instrumentos
                FROM Laboratorios L
                LEFT JOIN Instrumento I ON L.idlaboratorios = I.laboratorioid
                GROUP BY L.idlaboratorios, L.nombrelaboratorios, L."pisoLaboratorios", L.estadolaboratorios
                ORDER BY L.idlaboratorios ASC
            """
            cursor.execute(query)
            return [Laboratorio(idLaboratorios=l[0], nombreLaboratorios=l[1], pisoLaboratorios=l[2], estadoLaboratorios=l[3], instrument_count=l[4]) for l in cursor.fetchall()]
        except Exception as e:
            if "no existe la relación" in str(e).lower() or "instrumento" in str(e).lower():
                try:
                    cursor.execute('SELECT idlaboratorios, nombrelaboratorios, "pisoLaboratorios", estadolaboratorios FROM Laboratorios ORDER BY idlaboratorios ASC')
                    return [Laboratorio(idLaboratorios=l[0], nombreLaboratorios=l[1], pisoLaboratorios=l[2], estadoLaboratorios=l[3], instrument_count=0) for l in cursor.fetchall()]
                except:
                    return []
            print(f"🔴 Error SQL (get_all_laboratorios): {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def create_laboratorio(nombre, piso):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            check_query = """
                SELECT 
                    idlaboratorios 
                FROM Laboratorios 
                WHERE LOWER(nombrelaboratorios) = LOWER(%s)
            """
            cursor.execute(check_query, (nombre.strip(),))
            if cursor.fetchone():
                return "exists"

            query = """
                INSERT INTO Laboratorios (nombrelaboratorios, "pisoLaboratorios", estadolaboratorios) 
                VALUES (%s, %s, 'disponible') 
                RETURNING idlaboratorios
            """
            cursor.execute(query, (nombre.strip(), piso.strip()))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        except Exception as e:
            print(f"🔴 Error SQL (create_laboratorio): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def update_laboratorio(id_laboratorio, nuevo_nombre, nuevo_piso):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            check_query = 'SELECT idlaboratorios FROM Laboratorios WHERE LOWER(nombrelaboratorios) = LOWER(%s) AND idlaboratorios <> %s'
            cursor.execute(check_query, (nuevo_nombre.strip(), id_laboratorio))
            if cursor.fetchone():
                return "exists"
            
            query = 'UPDATE Laboratorios SET nombrelaboratorios = %s, "pisoLaboratorios" = %s WHERE idlaboratorios = %s'
            cursor.execute(query, (nuevo_nombre.strip(), nuevo_piso.strip(), id_laboratorio))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (update_laboratorio): {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def toggle_status(id_laboratorio, current_status):
        conn = DatabaseConnection.get_connection()
        if not conn: return False
        try:
            new_status = 'no disponible' if current_status.lower() == 'disponible' else 'disponible'
            cursor = conn.cursor()
            query = 'UPDATE Laboratorios SET estadolaboratorios = %s WHERE idlaboratorios = %s'
            cursor.execute(query, (new_status, id_laboratorio))
            conn.commit()
            return True
        except Exception as e:
            print(f"🔴 Error SQL (toggle_status): {e}")
            return False
        finally:
            if conn: conn.close()
