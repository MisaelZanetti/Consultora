import mysql.connector


class ConexionBaseDatos:
    def __init__(
        self,
        host: str = "localhost",
        puerto: int = 5000,
        usuario: str = "root",
        contrasena: str = "Mz200509#",
        base_datos: str = "consultora",
    ):
        self.host = host
        self.puerto = puerto
        self.usuario = usuario
        self.contrasena = contrasena
        self.base_datos = base_datos
        self._conexion = None

    def conectar(self):
        try:
            self._conexion = mysql.connector.connect(
                host=self.host,
                port=self.puerto,
                user=self.usuario,
                password=self.contrasena,
                database=self.base_datos,
                use_pure=True,
            )
            if self._conexion.is_connected():
                return self._conexion
        except Exception as ex:
            print(f"[BD] Conexión errónea: {ex}")
        return None

    def desconectar(self):
        if self._conexion and self._conexion.is_connected():
            self._conexion.close()
            self._conexion = None

    def __enter__(self):
        return self.conectar()

    def __exit__(self, tipo_exc, val_exc, tb_exc):
        self.desconectar()
        return False


def conectar_bd():
    return ConexionBaseDatos().conectar()
