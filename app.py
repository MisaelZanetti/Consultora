import flet as ft
from database import DatabaseConnection
from login_screen import LoginScreen
from main_screen import MainScreen

class App:
    """Controlador principal de la aplicación."""

    TITLE  = "Sistema de Consultora"
    WIDTH  = 1100
    HEIGHT = 700

    def __init__(self, page: ft.Page):
        self.page = page
        self.conn = None
        self._configurar_pagina()
        self._conectar_db()
        self.mostrar_login()

    # ── Configuración inicial ───────────────────────────────────────────────

    def _configurar_pagina(self):
        self.page.title         = self.TITLE
        self.page.window_width  = self.WIDTH
        self.page.window_height = self.HEIGHT
        self.page.scroll        = ft.ScrollMode.AUTO

    def _conectar_db(self):
        self.conn = DatabaseConnection().connect()

    # ── Navegación ─────────────────────────────────────────────────────────

    def mostrar_login(self):
        self.page.controls.clear()
        self.page.add(
            LoginScreen(self.page, self.conn, on_login_ok=self.mostrar_app).build()
        )
        self.page.update()

    def mostrar_app(self, usuario: dict):
        self.page.controls.clear()
        self.page.add(
            MainScreen(self.page, self.conn, usuario, on_logout=self.mostrar_login).build()
        )
        self.page.update()


# ── Punto de entrada ──────────────────────────────────────────────────────────

def main(page: ft.Page):
    App(page)


ft.app(target=main)
