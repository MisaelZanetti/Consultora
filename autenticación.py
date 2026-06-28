class ServicioAutenticacion:
    def __init__(self, conn):
        self.conn = conn

    def iniciar_sesion(self, nombre_usuario: str, contrasena: str) -> dict | None:
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
                (nombre_usuario, contrasena),
            )
            fila = cursor.fetchone()
            cursor.close()
            return fila
        except Exception as ex:
            print(f"[AUTH] Error: {ex}")
            return None


def login(conn, nombre_usuario: str, contrasena: str) -> dict | None:
    return ServicioAutenticacion(conn).iniciar_sesion(nombre_usuario, contrasena)
