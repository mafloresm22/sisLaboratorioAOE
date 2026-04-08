import os
import psycopg2
from dotenv import load_dotenv
from utils.paths import get_resource_path

env_path = get_resource_path(".env")
load_dotenv(dotenv_path=env_path)

class DatabaseConnection:
    @staticmethod
    def get_connection():
        try:
            conexion = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            return conexion
        except Exception as e:
            print(f"🔴 Error al conectar a la base de datos: {e}")
            return None

    @staticmethod
    def execute_query(query, params=None):
        """Ejecuta una consulta SQL genérica."""
        conn = DatabaseConnection.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
            except Exception as e:
                print(f"🔴 Error ejecutando query: {e}")
                conn.rollback()
            finally:
                conn.close()
        return None
