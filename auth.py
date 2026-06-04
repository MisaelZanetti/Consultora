class AuthService:
    """Servicio de autenticación contra la base de datos."""

    def __init__(self, conn):
        self.conn = conn

    def login(self, username: str, password: str) -> dict | None:
        """
        Verifica credenciales en texto plano.
        Retorna un dict con los datos del usuario o None si falla.
        """
        try:
            cursor = self.conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT u.id_usuario, u.username, u.rol, u.cod_empleado,
                       c.nombre AS nombre_empleado
                FROM usuario u
                LEFT JOIN consultor c ON c.cod_empleado = u.cod_empleado
                WHERE u.username = %s
                  AND u.password = %s
                  AND u.activo   = 1
                """,
                (username, password),
            )
            row = cursor.fetchone()
            cursor.close()
            return row
        except Exception as ex:
            print(f"[AUTH] Error: {ex}")
            return None


# ── Helper de módulo (compatibilidad con auth.login() existente) ──────────────

def login(conn, username: str, password: str) -> dict | None:
    return AuthService(conn).login(username, password)
