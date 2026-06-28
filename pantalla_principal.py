import flet as ft
from vistas import (
    VistaConsultores,
    VistaCategorias,
    VistaEmpresas,
    VistaProyectos,
    VistaVentas,
)
from tema import C, T, E, R, insignia, divisor


class PantallaPrincipal:
    def __init__(self, pagina: ft.Page, conn, usuario: dict, al_cerrar):
        self.pagina   = pagina
        self.conn     = conn
        self.usuario  = usuario
        self.al_cerrar = al_cerrar

        self.es_admin: bool = usuario["rol"] == "admin"
        self.nombre_display: str = usuario.get("nombre_empleado") or usuario["username"]

        self._contenido = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        self._mostrar_bienvenida()

    def _mostrar_vista(self, clase_vista, titulo: str):
        vista_col = clase_vista(self.conn, self.usuario).build()
        self._contenido.controls.clear()
        self._contenido.controls.extend([
            ft.Container(
                content=ft.Text(titulo, size=T.DISPLAY,
                                weight=ft.FontWeight.W_700, color=C.TEXTO),
                padding=ft.padding.only(bottom=E.CH),
            ),
            divisor(),
            ft.Container(content=vista_col, padding=ft.padding.only(top=E.MD)),
        ])
        self.pagina.update()

    def _mostrar_bienvenida(self):
        self._contenido.controls.clear()
        self._contenido.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.WAVING_HAND_OUTLINED,
                                            size=36, color=C.PRIMARIO),
                            bgcolor=C.PRIMARIO_FONDO,
                            border_radius=R.MD,
                            padding=E.MD,
                            width=64, height=64,
                        ),
                        ft.Text(f"Bienvenido/a, {self.nombre_display}",
                                size=T.DISPLAY, weight=ft.FontWeight.W_700,
                                color=C.TEXTO),
                        ft.Text("Seleccioná una sección desde el menú superior.",
                                size=T.CUERPO, color=C.TEXTO_SEC),
                    ],
                    spacing=E.MD,
                ),
                padding=ft.padding.only(top=E.XGD),
            )
        )

    def _menu_archivo(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Archivo", size=T.PEQUEÑO,
                                color=C.TEXTO, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=C.TEXTO_SEC),
                    ],
                    spacing=2, tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=E.CH, vertical=E.XCH),
            ),
            items=[
                ft.PopupMenuItem(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.LOGOUT, size=16, color=C.TEXTO_SEC),
                        ft.Text("Cerrar sesión", size=T.CUERPO, color=C.TEXTO),
                    ], spacing=E.CH),
                    on_click=lambda _: self.al_cerrar(),
                ),
            ],
        )

    def _menu_herramientas(self) -> ft.PopupMenuButton:
        def elemento(texto, icono, vista, titulo):
            return ft.PopupMenuItem(
                content=ft.Row(controls=[
                    ft.Icon(icono, size=16, color=C.TEXTO_SEC),
                    ft.Text(texto, size=T.CUERPO, color=C.TEXTO),
                ], spacing=E.CH),
                on_click=lambda _: self._mostrar_vista(vista, titulo),
            )

        elementos = [
            elemento("Consultores",       ft.Icons.PEOPLE_OUTLINE,        VistaConsultores, "Consultores"),
            elemento("Proyectos",         ft.Icons.FOLDER_OPEN_OUTLINED,  VistaProyectos,   "Proyectos"),
            elemento("Ventas",            ft.Icons.RECEIPT_LONG_OUTLINED, VistaVentas,      "Ventas"),
        ]
        if self.es_admin:
            elementos.insert(1, elemento("Categorías",       ft.Icons.LABEL_OUTLINE,     VistaCategorias, "Categorías"))
            elementos.insert(3, elemento("Empresas Clientes",ft.Icons.BUSINESS_OUTLINED, VistaEmpresas,   "Empresas Clientes"))

        return ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Herramientas", size=T.PEQUEÑO,
                                color=C.TEXTO, weight=ft.FontWeight.W_500),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16, color=C.TEXTO_SEC),
                    ],
                    spacing=2, tight=True,
                ),
                padding=ft.padding.symmetric(horizontal=E.CH, vertical=2),
            ),
            items=elementos,
        )

    def _btn(self, icono, tooltip, vista, titulo) -> ft.IconButton:
        return ft.IconButton(
            icon=icono,
            tooltip=tooltip,
            icon_color=C.TEXTO_SEC,
            icon_size=20,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=R.CH),
                overlay_color=C.PRIMARIO_FONDO,
            ),
            on_click=lambda _: self._mostrar_vista(vista, titulo),
        )

    def _botones_rapidos(self) -> list[ft.IconButton]:
        botones = [
            self._btn(ft.Icons.PEOPLE_OUTLINE,        "Consultores",       VistaConsultores, "Consultores"),
            self._btn(ft.Icons.FOLDER_OPEN_OUTLINED,  "Proyectos",         VistaProyectos,   "Proyectos"),
            self._btn(ft.Icons.RECEIPT_LONG_OUTLINED, "Ventas",            VistaVentas,      "Ventas"),
        ]
        if self.es_admin:
            botones.insert(1, self._btn(ft.Icons.LABEL_OUTLINE,      "Categorías",        VistaCategorias, "Categorías"))
            botones.insert(3, self._btn(ft.Icons.BUSINESS_OUTLINED,  "Empresas Clientes", VistaEmpresas,   "Empresas Clientes"))
        return botones

    def build(self) -> ft.Column:
        es_admin = self.usuario["rol"] == "admin"
        color_insignia = C.PRIMARIO if es_admin else C.EXITO

        barra_superior = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.BUSINESS_CENTER_OUTLINED,
                                                size=18, color=C.PRIMARIO),
                                bgcolor=C.PRIMARIO_FONDO,
                                border_radius=R.CH,
                                padding=ft.padding.symmetric(horizontal=6, vertical=4),
                            ),
                            ft.Text("Consultora", size=T.CUERPO,
                                    weight=ft.FontWeight.W_700, color=C.TEXTO),
                        ],
                        spacing=E.CH,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(width=E.MD),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self._menu_archivo(),
                                self._menu_herramientas(),
                            ],
                            spacing=E.XCH,
                        ),
                        border=ft.border.all(1, C.BORDE),
                        border_radius=R.CH,
                        padding=ft.padding.symmetric(horizontal=E.XCH, vertical=2),
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row(controls=self._botones_rapidos(), spacing=2),
                        border=ft.border.all(1, C.BORDE),
                        border_radius=R.CH,
                        padding=ft.padding.symmetric(horizontal=E.XCH, vertical=2),
                    ),
                    ft.Container(width=E.CH),
                    ft.Row(
                        controls=[
                            ft.Text(f"👤  {self.nombre_display}",
                                    size=T.PEQUEÑO, color=C.TEXTO_SEC),
                            insignia(self.usuario["rol"].upper(), color_fondo=color_insignia),
                        ],
                        spacing=E.CH,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=E.XCH,
            ),
            bgcolor=C.SUPERFICIE,
            border=ft.border.only(bottom=ft.BorderSide(1, C.BORDE)),
            padding=ft.padding.symmetric(horizontal=E.GD, vertical=E.CH),
            height=52,
        )

        envoltura_contenido = ft.Container(
            content=self._contenido,
            expand=True,
            padding=ft.padding.symmetric(horizontal=E.XGD, vertical=E.GD),
            bgcolor=C.FONDO,
        )

        return ft.Column(
            controls=[barra_superior, envoltura_contenido],
            expand=True,
            spacing=0,
        )


def pantalla_principal(pagina, conn, usuario, al_cerrar) -> ft.Column:
    return PantallaPrincipal(pagina, conn, usuario, al_cerrar).build()
