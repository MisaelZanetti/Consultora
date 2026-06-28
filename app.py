import flet as ft
from base_datos import ConexionBaseDatos
from pantalla_inicioSesion import PantallaLogin
from pantalla_principal import PantallaPrincipal
from tema import C


class Aplicacion:
    TITULO = "Sistema de Consultora"
    ANCHO  = 1200
    ALTO   = 740

    def __init__(self, pagina: ft.Page):
        self.pagina = pagina
        self.conn = None
        self._configurar_pagina()
        self._conectar_bd()
        self.mostrar_login()

    def _configurar_pagina(self):
        self.pagina.title         = self.TITULO
        self.pagina.window_width  = self.ANCHO
        self.pagina.window_height = self.ALTO
        self.pagina.bgcolor       = C.FONDO
        self.pagina.padding       = 0
        self.pagina.theme_mode    = ft.ThemeMode.DARK
        self.pagina.theme = ft.Theme(
            color_scheme_seed=C.PRIMARIO,
            use_material3=True,
        )
        self.pagina.dark_theme = ft.Theme(
            color_scheme_seed=C.PRIMARIO,
            use_material3=True,
        )

    def _conectar_bd(self):
        self.conn = ConexionBaseDatos().conectar()

    def mostrar_login(self):
        self.pagina.bgcolor = C.FONDO
        self.pagina.controls.clear()
        self.pagina.add(PantallaLogin(self.pagina, self.conn, al_iniciar=self.mostrar_app).build())
        self.pagina.update()

    def mostrar_app(self, usuario: dict):
        self.pagina.bgcolor = C.FONDO
        self.pagina.controls.clear()
        self.pagina.add(PantallaPrincipal(self.pagina, self.conn, usuario, al_cerrar=self.mostrar_login).build())
        self.pagina.update()


def main(pagina: ft.Page):
    Aplicacion(pagina)


ft.app(target=main)
