import flet as ft
from auth import AuthService


class LoginScreen:
    """Pantalla de inicio de sesión."""

    def __init__(self, page: ft.Page, conn, on_login_ok):
        self.page = page
        self.conn = conn
        self.on_login_ok = on_login_ok
        self._auth = AuthService(conn) if conn else None

        # ── Controles ──────────────────────────────────────────────────────
        self.campo_user = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON,
            width=320,
            autofocus=True,
            on_submit=self._intentar_login,
        )
        self.campo_pass = ft.TextField(
            label="Contraseña",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            width=320,
            on_submit=self._intentar_login,
        )
        self.error_txt = ft.Text("", color=ft.Colors.RED, size=13)

    # ── Lógica ─────────────────────────────────────────────────────────────

    def _mostrar_error(self, mensaje: str):
        self.error_txt.value = mensaje
        self.page.update()

    def _intentar_login(self, _e=None):
        self.error_txt.value = ""

        usuario = (self.campo_user.value or "").strip()
        password = self.campo_pass.value or ""

        if not usuario or not password:
            return self._mostrar_error("Completá usuario y contraseña.")

        if self._auth is None:
            return self._mostrar_error("No hay conexión a la base de datos.")

        datos = self._auth.login(usuario, password)
        if datos:
            self.on_login_ok(datos)
        else:
            self.campo_pass.value = ""
            self._mostrar_error("Usuario o contraseña incorrectos.")

    # ── UI ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Column:
        return ft.Column(
            controls=[
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.BUSINESS_CENTER, size=48, color=ft.Colors.BLUE),
                                ft.Text("Sistema de Consultora", size=22, weight=ft.FontWeight.BOLD),
                                ft.Text("Iniciá sesión para continuar", size=13, color=ft.Colors.GREY_600),
                                ft.Divider(),
                                self.campo_user,
                                self.campo_pass,
                                self.error_txt,
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.LOGIN),
                                            ft.Text("Ingresar"),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=8,
                                    ),
                                    width=320,
                                    on_click=self._intentar_login,
                                ),
                            ],
                            spacing=16,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=40,
                    ),
                    elevation=6,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )


# ── Helper de módulo (compatibilidad con app.py existente) ────────────────────

def pantalla_login(page, conn, on_login_ok) -> ft.Column:
    return LoginScreen(page, conn, on_login_ok).build()
