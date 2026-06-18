import flet as ft

# ── Clase base ────────────────────────────────────────────────────────────────

class BaseVista:
    """Clase base para todas las vistas de tabla."""

    TABLE_STYLE = dict(
        border=ft.border.all(1, ft.Colors.GREY_300),
        heading_row_color=ft.Colors.BLUE_50,
    )

    def __init__(self, conn, usuario=None):
        self.conn = conn
        self.usuario = usuario
        self._todos_los_rows = []   # caché para fetchall
        self._tabla: ft.DataTable | None = None

    def _fetch(self, sql: str, params=()) -> list:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def _hacer_filas(self, rows: list) -> list[ft.DataRow]:
        """Convierte tuplas de BD en DataRow. Debe implementarse en cada subclase."""
        raise NotImplementedError

    def _columnas(self) -> list[ft.DataColumn]:
        """Devuelve las columnas de la tabla. Debe implementarse en cada subclase."""
        raise NotImplementedError

    def _sql_all(self) -> str:
        """Query base para traer todos los registros."""
        raise NotImplementedError

    # ── Controles de filtrado ─────────────────────────────────────────────────

    def _barra_filtros(
        self,
        *,
        dropdown_label: str,
        dropdown_opciones: list[str],
        on_dropdown: callable,
        on_fetchone: callable,
        on_fetchall: callable,
        campo_busqueda_label: str = "Buscar...",
    ) -> ft.Row:
        """
        Devuelve una fila con:
          • PopupMenuButton → filtra por categoría / campo clave (compatible Flet 0.84)
          • TextField       → fetchone (busca un registro por texto)
          • Botón           → fetchall (limpia filtros, muestra todo)
        """
        # Etiqueta dinámica del botón de filtro
        self._dd_label = ft.Text(dropdown_label if dropdown_label != "—" else "Filtrar")

        def _hacer_item(opcion: str):
            def _handler(_e, op=opcion):
                self._dd_label.value = op
                self._dd_label.update()
                on_dropdown(op)
            return ft.PopupMenuItem(content=ft.Text(opcion), on_click=_handler)

        items = [_hacer_item(o) for o in dropdown_opciones]

        self._dd_btn = ft.PopupMenuButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FILTER_LIST, size=16),
                    self._dd_label,
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=16),
                ],
                spacing=4,
                tight=True,
            ),
            items=items if items else [ft.PopupMenuItem(content=ft.Text("Sin opciones"))],
        )

        self._campo_busqueda = ft.TextField(
            label=campo_busqueda_label,
            prefix_icon=ft.Icons.SEARCH,
            width=240,
            on_submit=lambda e: on_fetchone(e.control.value),
        )

        def _reset(_):
            self._dd_label.value = dropdown_label if dropdown_label != "—" else "Filtrar"
            self._dd_label.update()
            on_fetchall()

        return ft.Row(
            controls=[
                ft.Container(
                    content=self._dd_btn,
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                ) if items else ft.Container(),
                self._campo_busqueda,
                ft.IconButton(
                    icon=ft.Icons.SEARCH,
                    tooltip="Buscar (fetchone)",
                    on_click=lambda _: on_fetchone(self._campo_busqueda.value),
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Mostrar todo (fetchall)",
                    on_click=_reset,
                ),
            ],
            spacing=8,
            wrap=True,
        )

    def _actualizar_tabla(self, rows: list):
        """Reemplaza las filas de self._tabla y refresca la UI."""
        self._tabla.rows = self._hacer_filas(rows)
        self._tabla.update()

    def build(self) -> ft.Column:
        raise NotImplementedError

    def __call__(self) -> ft.Column:
        return self.build()


# ── VistaConsultores ──────────────────────────────────────────────────────────

class VistaConsultores(BaseVista):

    _SQL = """
        SELECT c.cod_empleado, c.nombre, c.sueldo,
               cat.nombre AS categoria, j.nombre AS jefe
        FROM consultor c
        JOIN categoria cat ON cat.id_categoria = c.id_categoria
        LEFT JOIN consultor j ON j.cod_empleado = c.jefe
        {where}
        ORDER BY c.cod_empleado
    """

    def _columnas(self):
        return [
            ft.DataColumn(ft.Text("Cód.")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Sueldo")),
            ft.DataColumn(ft.Text("Categoría")),
            ft.DataColumn(ft.Text("Jefe")),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r[0]))),
                ft.DataCell(ft.Text(r[1])),
                ft.DataCell(ft.Text(f"${r[2]:,.2f}")),
                ft.DataCell(ft.Text(r[3])),
                ft.DataCell(ft.Text(r[4] or "—")),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _categorias(self) -> list[str]:
        rows = self._fetch("SELECT nombre FROM categoria ORDER BY nombre")
        return [r[0] for r in rows]

    def _on_dropdown(self, categoria: str):
        if not categoria:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE cat.nombre = %s"),
            (categoria,),
        )
        self._actualizar_tabla(rows)

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE c.nombre LIKE %s OR c.cod_empleado LIKE %s"),
            (f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._campo_busqueda.value = ""
        self._campo_busqueda.update()
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todos_los_rows),
            **self.TABLE_STYLE,
        )
        barra = self._barra_filtros(
            dropdown_label="Categoría",
            dropdown_opciones=self._categorias(),
            on_dropdown=self._on_dropdown,
            on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por nombre o cód.",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=10)


# ── VistaCategorias ───────────────────────────────────────────────────────────

class VistaCategorias(BaseVista):

    _SQL = """
        SELECT id_categoria, nombre, salario_rec
        FROM categoria
        {where}
        ORDER BY id_categoria
    """

    def _columnas(self):
        return [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Salario Recomendado")),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r[0]))),
                ft.DataCell(ft.Text(r[1])),
                ft.DataCell(ft.Text(f"${r[2]:,.2f}")),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _on_dropdown(self, _valor):
        pass  # Categorías no tiene subclasificación; el dropdown queda reservado

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE nombre LIKE %s"),
            (f"%{texto}%",),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._campo_busqueda.value = ""
        self._campo_busqueda.update()
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todos_los_rows),
            **self.TABLE_STYLE,
        )
        barra = self._barra_filtros(
            dropdown_label="—",          # sin uso aquí
            dropdown_opciones=[],
            on_dropdown=self._on_dropdown,
            on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por nombre",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=10)


# ── VistaEmpresas ─────────────────────────────────────────────────────────────

class VistaEmpresas(BaseVista):

    _SQL = """
        SELECT ec.cif, ec.nombre, ec.direccion,
               GROUP_CONCAT(tc.telefono SEPARATOR ' / ') AS telefonos
        FROM empresa_cliente ec
        LEFT JOIN telefono_cliente tc ON tc.cif = ec.cif
        {where}
        GROUP BY ec.cif, ec.nombre, ec.direccion
        ORDER BY ec.nombre
    """

    def _columnas(self):
        return [
            ft.DataColumn(ft.Text("CIF")),
            ft.DataColumn(ft.Text("Empresa")),
            ft.DataColumn(ft.Text("Dirección")),
            ft.DataColumn(ft.Text("Teléfonos")),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(r[0])),
                ft.DataCell(ft.Text(r[1])),
                ft.DataCell(ft.Text(r[2])),
                ft.DataCell(ft.Text(r[3] or "—")),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _on_dropdown(self, _valor):
        pass  # reservado para filtro futuro por ciudad/país si la BD lo soporta

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE ec.nombre LIKE %s OR ec.cif LIKE %s"),
            (f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._campo_busqueda.value = ""
        self._campo_busqueda.update()
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todos_los_rows),
            **self.TABLE_STYLE,
        )
        barra = self._barra_filtros(
            dropdown_label="—",
            dropdown_opciones=[],
            on_dropdown=self._on_dropdown,
            on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por nombre o CIF",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=10)


# ── VistaProyectos ────────────────────────────────────────────────────────────

class VistaProyectos(BaseVista):

    _SQL = """
        SELECT id_proyecto, descripcion, coste
        FROM proyecto
        {where}
        ORDER BY id_proyecto
    """

    def _columnas(self):
        return [
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Descripción")),
            ft.DataColumn(ft.Text("Coste Interno")),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r[0]))),
                ft.DataCell(ft.Text(r[1] or "—")),
                ft.DataCell(ft.Text(f"${r[2]:,.2f}")),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    def _on_dropdown(self, _valor):
        pass

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE descripcion LIKE %s OR id_proyecto LIKE %s"),
            (f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._campo_busqueda.value = ""
        self._campo_busqueda.update()
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todos_los_rows),
            **self.TABLE_STYLE,
        )
        barra = self._barra_filtros(
            dropdown_label="—",
            dropdown_opciones=[],
            on_dropdown=self._on_dropdown,
            on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por descripción o ID",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=10)


# ── VistaVentas ───────────────────────────────────────────────────────────────

class VistaVentas(BaseVista):

    _SQL = """
        SELECT v.id_venta, ec.nombre, p.id_proyecto,
               c.nombre, v.precio, v.fecha_inicio, v.fecha_fin
        FROM venta v
        JOIN empresa_cliente ec ON ec.cif         = v.cif
        JOIN proyecto         p  ON p.id_proyecto  = v.id_proyecto
        JOIN consultor        c  ON c.cod_empleado = v.cod_empleado
        {where}
        ORDER BY v.id_venta
    """

    def _columnas(self):
        return [
            ft.DataColumn(ft.Text("ID Venta")),
            ft.DataColumn(ft.Text("Empresa")),
            ft.DataColumn(ft.Text("Proy.")),
            ft.DataColumn(ft.Text("Consultor")),
            ft.DataColumn(ft.Text("Precio")),
            ft.DataColumn(ft.Text("Inicio")),
            ft.DataColumn(ft.Text("Fin")),
        ]

    def _hacer_filas(self, rows):
        return [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(r[0]))),
                ft.DataCell(ft.Text(r[1])),
                ft.DataCell(ft.Text(str(r[2]))),
                ft.DataCell(ft.Text(r[3])),
                ft.DataCell(ft.Text(f"${r[4]:,.2f}")),
                ft.DataCell(ft.Text(str(r[5]) if r[5] else "—")),
                ft.DataCell(ft.Text(str(r[6]) if r[6] else "—")),
            ]) for r in rows
        ]

    def _sql_all(self):
        return self._SQL.format(where="")

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _empresas(self) -> list[str]:
        rows = self._fetch("SELECT nombre FROM empresa_cliente ORDER BY nombre")
        return [r[0] for r in rows]

    def _on_dropdown(self, empresa: str):
        if not empresa:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE ec.nombre = %s"),
            (empresa,),
        )
        self._actualizar_tabla(rows)

    def _on_fetchone(self, texto: str):
        texto = (texto or "").strip()
        if not texto:
            return
        rows = self._fetch(
            self._SQL.format(where="WHERE v.id_venta LIKE %s OR c.nombre LIKE %s OR ec.nombre LIKE %s"),
            (f"%{texto}%", f"%{texto}%", f"%{texto}%"),
        )
        self._actualizar_tabla(rows)

    def _on_fetchall(self):
        self._campo_busqueda.value = ""
        self._campo_busqueda.update()
        self._actualizar_tabla(self._todos_los_rows)

    def build(self) -> ft.Column:
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todos_los_rows),
            **self.TABLE_STYLE,
        )
        barra = self._barra_filtros(
            dropdown_label="Empresa",
            dropdown_opciones=self._empresas(),
            on_dropdown=self._on_dropdown,
            on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            campo_busqueda_label="Buscar por ID, consultor o empresa",
        )
        return ft.Column(controls=[barra, self._tabla], spacing=10)


# ── Helpers de módulo (compatibilidad con main_screen.py existente) ───────────

def vista_consultores(conn, u):  return VistaConsultores(conn, u).build()
def vista_categorias(conn, u):   return VistaCategorias(conn, u).build()
def vista_empresas(conn, u):     return VistaEmpresas(conn, u).build()
def vista_proyectos(conn, u):    return VistaProyectos(conn, u).build()
def vista_ventas(conn, u):       return VistaVentas(conn, u).build()