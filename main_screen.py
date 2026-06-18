import flet as ft
from vistas import (
    VistaConsultores,
    VistaCategorias,
    VistaEmpresas,
    VistaProyectos,
    VistaVentas,
)


class MainScreen:
    """Pantalla principal de la aplicación."""

    def __init__(self, page: ft.Page, conn, usuario: dict, on_logout):
        self.page = page
        self.conn = conn
        self.usuario = usuario
        self.on_logout = on_logout

        self.es_admin: bool = usuario["rol"] == "admin"
        self.nombre_display: str = usuario.get("nombre_empleado") or usuario["username"]

        # Área de contenido central (se reemplaza al navegar)
        self._contenido = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        self._mostrar_bienvenida()

    # ── Navegación ─────────────────────────────────────────────────────────

    def _mostrar_vista(self, clase_vista, titulo: str):
        # Las vistas ahora devuelven ft.Column (con barra de filtros + tabla)
        vista_col = clase_vista(self.conn, self.usuario).build()
        self._contenido.controls.clear()
        self._contenido.controls.extend([
            ft.Text(titulo, size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            vista_col,
        ])
        self.page.update()

    def _mostrar_bienvenida(self):
        self._contenido.controls.clear()
        self._contenido.controls.append(
            ft.Column(
                controls=[
                    ft.Text(
                        f"Bienvenido/a, {self.nombre_display}!",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text("Seleccioná una opción del menú o de la barra de acceso rápido."),
                ],
                spacing=10,
            )
        )

    # ── Construcción del menú ───────────────────────────────────────────────

    def _menu_archivo(self) -> ft.PopupMenuButton:
        return ft.PopupMenuButton(
            content=ft.Text("Archivo"),
            items=[
                ft.PopupMenuItem(
                    content=ft.Text("Cerrar sesión"),
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda _: self.on_logout(),
                ),
            ],
        )

    def _menu_herramientas(self) -> ft.PopupMenuButton:
        items = [
            ft.PopupMenuItem(
                content=ft.Text("Consultores"), icon=ft.Icons.PEOPLE,
                on_click=lambda _: self._mostrar_vista(VistaConsultores, "Consultores"),
            ),
            ft.PopupMenuItem(
                content=ft.Text("Proyectos"), icon=ft.Icons.FOLDER_SPECIAL,
                on_click=lambda _: self._mostrar_vista(VistaProyectos, "Proyectos"),
            ),
            ft.PopupMenuItem(
                content=ft.Text("Ventas"), icon=ft.Icons.POINT_OF_SALE,
                on_click=lambda _: self._mostrar_vista(VistaVentas, "Ventas"),
            ),
        ]
        if self.es_admin:
            items.insert(1, ft.PopupMenuItem(
                content=ft.Text("Categorías"), icon=ft.Icons.GRADE,
                on_click=lambda _: self._mostrar_vista(VistaCategorias, "Categorías"),
            ))
            items.insert(3, ft.PopupMenuItem(
                content=ft.Text("Empresas Clientes"), icon=ft.Icons.BUSINESS,
                on_click=lambda _: self._mostrar_vista(VistaEmpresas, "Empresas Clientes"),
            ))
        return ft.PopupMenuButton(content=ft.Text("Herramientas"), items=items)

    def _botones_rapidos(self) -> list[ft.IconButton]:
        botones = [
            ft.IconButton(icon=ft.Icons.PEOPLE,        tooltip="Consultores",
                          on_click=lambda _: self._mostrar_vista(VistaConsultores, "Consultores")),
            ft.IconButton(icon=ft.Icons.FOLDER_SPECIAL, tooltip="Proyectos",
                          on_click=lambda _: self._mostrar_vista(VistaProyectos, "Proyectos")),
            ft.IconButton(icon=ft.Icons.POINT_OF_SALE,  tooltip="Ventas",
                          on_click=lambda _: self._mostrar_vista(VistaVentas, "Ventas")),
        ]
        if self.es_admin:
            botones.insert(1, ft.IconButton(icon=ft.Icons.GRADE, tooltip="Categorías",
                                            on_click=lambda _: self._mostrar_vista(VistaCategorias, "Categorías")))
            botones.insert(3, ft.IconButton(icon=ft.Icons.BUSINESS, tooltip="Empresas Clientes",
                                            on_click=lambda _: self._mostrar_vista(VistaEmpresas, "Empresas Clientes")))
        return botones

    def _badge_rol(self) -> ft.Container:
        return ft.Container(
            content=ft.Text(
                self.usuario["rol"].upper(),
                size=11,
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor=ft.Colors.BLUE if self.es_admin else ft.Colors.GREEN,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
        )

    # ── UI ─────────────────────────────────────────────────────────────────

    def build(self) -> ft.Column:
        barra_menu = ft.Row(
            controls=[
                self._menu_archivo(),
                self._menu_herramientas(),
                ft.Container(expand=True),
                ft.Text(f"👤 {self.nombre_display}", size=13),
                self._badge_rol(),
            ],
            spacing=10,
        )

        return ft.Column(
            controls=[
                barra_menu,
                ft.Divider(height=1),
                ft.Row(controls=self._botones_rapidos(), spacing=4),
                ft.Divider(height=1),
                self._contenido,
            ],
            expand=True,
        )


# ── Helper de módulo (compatibilidad con app.py existente) ────────────────────

def pantalla_principal(page, conn, usuario, on_logout) -> ft.Column:
    return MainScreen(page, conn, usuario, on_logout).build()