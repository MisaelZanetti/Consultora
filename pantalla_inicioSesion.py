import flet as ft
from autenticación import ServicioAutenticacion
from tema import C, T, E, R, divisor


class PantallaLogin:
    _FONDO      = "#0F1117"
    _SUPERFICIE = "#1A1D27"
    _BORDE      = "#2A2D3A"
    _PRIMARIO   = "#3B82F6"
    _PRIMARIO_O = "#2563EB"
    _TEXTO      = "#F1F5F9"
    _TEXTO_SEC  = "#64748B"
    _ERROR      = "#F87171"

    def __init__(self, pagina: ft.Page, conn, al_iniciar):
        self.pagina = pagina
        self.conn = conn
        self.al_iniciar = al_iniciar
        self._auth = ServicioAutenticacion(conn) if conn else None

        self.campo_usuario = ft.TextField(
            label="Usuario",
            label_style=ft.TextStyle(size=13, color=self._TEXTO_SEC),
            prefix_icon=ft.Icons.PERSON_OUTLINE,
            autofocus=True,
            border_color=self._BORDE,
            focused_border_color=self._PRIMARIO,
            cursor_color=self._PRIMARIO,
            bgcolor=self._SUPERFICIE,
            text_style=ft.TextStyle(size=14, color=self._TEXTO),
            filled=True,
            on_submit=self._intentar_login,
        )
        self.campo_contrasena = ft.TextField(
            label="Contraseña",
            label_style=ft.TextStyle(size=13, color=self._TEXTO_SEC),
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            border_color=self._BORDE,
            focused_border_color=self._PRIMARIO,
            cursor_color=self._PRIMARIO,
            bgcolor=self._SUPERFICIE,
            text_style=ft.TextStyle(size=14, color=self._TEXTO),
            filled=True,
            on_submit=self._intentar_login,
        )
        self.texto_error = ft.Text("", color=self._ERROR, size=13)

    def _mostrar_error(self, mensaje: str):
        self.texto_error.value = mensaje
        self.pagina.update()

    def _intentar_login(self, _e=None):
        self.texto_error.value = ""
        nombre_usuario = (self.campo_usuario.value or "").strip()
        contrasena     = self.campo_contrasena.value or ""

        if not nombre_usuario or not contrasena:
            return self._mostrar_error("Completá usuario y contraseña.")
        if self._auth is None:
            return self._mostrar_error("Sin conexión a la base de datos.")

        datos = self._auth.iniciar_sesion(nombre_usuario, contrasena)
        if datos:
            self.al_iniciar(datos)
        else:
            self.campo_contrasena.value = ""
            self._mostrar_error("Usuario o contraseña incorrectos.")

    def build(self) -> ft.Container:
        tarjeta = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.BUSINESS_CENTER_OUTLINED,
                                    size=22, color=self._PRIMARIO,
                                ),
                                bgcolor="#1E3A5F",
                                border_radius=10,
                                padding=ft.padding.all(10),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Sistema de Consultora",
                                        size=18,
                                        weight=ft.FontWeight.W_700,
                                        color=self._TEXTO,
                                    ),
                                    ft.Text(
                                        "Iniciá sesión para continuar",
                                        size=12,
                                        color=self._TEXTO_SEC,
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Divider(color=self._BORDE, height=24),
                    self.campo_usuario,
                    self.campo_contrasena,
                    ft.Container(content=self.texto_error, height=18),
                    ft.Container(height=4),
                    ft.ElevatedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ARROW_FORWARD, size=18),
                                ft.Text("Ingresar", size=14, weight=ft.FontWeight.W_600),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        height=44,
                        style=ft.ButtonStyle(
                            bgcolor=self._PRIMARIO,
                            color=self._TEXTO,
                            shape=ft.RoundedRectangleBorder(radius=8),
                            elevation=0,
                            overlay_color=self._PRIMARIO_O,
                        ),
                        on_click=self._intentar_login,
                    ),
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            width=400,
            bgcolor=self._SUPERFICIE,
            border_radius=14,
            border=ft.border.all(1, self._BORDE),
            padding=ft.padding.symmetric(horizontal=36, vertical=32),
            shadow=ft.BoxShadow(
                blur_radius=40,
                color="#40000000",
                offset=ft.Offset(0, 8),
            ),
        )

        return ft.Container(
            content=ft.Column(
                controls=[tarjeta],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=self._FONDO,
            expand=True,
            alignment=ft.Alignment(0, 0),
        )


def pantalla_login(pagina, conn, al_iniciar) -> ft.Container:
    return PantallaLogin(pagina, conn, al_iniciar).build()
