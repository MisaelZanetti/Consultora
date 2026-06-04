import mysql.connector


class DatabaseConnection:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5000,
        user: str = "root",
        password: str = "Mz200509#",
        database: str = "consultora",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self._connection = None

    # ── Conexión ──────────────────────────────────────────────────────────────

    def connect(self):
        """Establece la conexión y la devuelve. Retorna None si falla."""
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                use_pure=True,
            )
            if self._connection.is_connected():
                return self._connection
        except Exception as ex:
            print(f"[DB] Conexión errónea: {ex}")
        return None

    def disconnect(self):
        """Cierra la conexión si está abierta."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            self._connection = None

    # ── Context manager (soporte para `with DatabaseConnection() as conn`) ───

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False


# ── Helper de módulo (compatibilidad con el resto del proyecto) ───────────────

def connect_to_db():
    """Crea una instancia y retorna la conexión activa."""
    return DatabaseConnection().connect()
