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

    def _fetch(self, sql: str, params=()) -> list:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def build(self) -> ft.DataTable:
        raise NotImplementedError

    # Permite llamar la clase como función: VistaXxx(conn, u) → ft.DataTable
    def __call__(self) -> ft.DataTable:
        return self.build()


# ── Vistas concretas ──────────────────────────────────────────────────────────

class VistaConsultores(BaseVista):

    def build(self) -> ft.DataTable:
        rows = self._fetch("""
            SELECT c.cod_empleado, c.nombre, c.sueldo,
                   cat.nombre AS categoria, j.nombre AS jefe
            FROM consultor c
            JOIN categoria cat ON cat.id_categoria = c.id_categoria
            LEFT JOIN consultor j ON j.cod_empleado = c.jefe
            ORDER BY c.cod_empleado
        """)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cód.")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Sueldo")),
                ft.DataColumn(ft.Text("Categoría")),
                ft.DataColumn(ft.Text("Jefe")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]))),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(f"${r[2]:,.2f}")),
                    ft.DataCell(ft.Text(r[3])),
                    ft.DataCell(ft.Text(r[4] or "—")),
                ]) for r in rows
            ],
            **self.TABLE_STYLE,
        )


class VistaCategorias(BaseVista):

    def build(self) -> ft.DataTable:
        rows = self._fetch(
            "SELECT id_categoria, nombre, salario_rec FROM categoria ORDER BY id_categoria"
        )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Salario Recomendado")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]))),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(f"${r[2]:,.2f}")),
                ]) for r in rows
            ],
            **self.TABLE_STYLE,
        )


class VistaEmpresas(BaseVista):

    def build(self) -> ft.DataTable:
        rows = self._fetch("""
            SELECT ec.cif, ec.nombre, ec.direccion,
                   GROUP_CONCAT(tc.telefono SEPARATOR ' / ') AS telefonos
            FROM empresa_cliente ec
            LEFT JOIN telefono_cliente tc ON tc.cif = ec.cif
            GROUP BY ec.cif, ec.nombre, ec.direccion
            ORDER BY ec.nombre
        """)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("CIF")),
                ft.DataColumn(ft.Text("Empresa")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfonos")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[0])),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(r[2])),
                    ft.DataCell(ft.Text(r[3] or "—")),
                ]) for r in rows
            ],
            **self.TABLE_STYLE,
        )


class VistaProyectos(BaseVista):

    def build(self) -> ft.DataTable:
        rows = self._fetch(
            "SELECT id_proyecto, descripcion, coste FROM proyecto ORDER BY id_proyecto"
        )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Coste Interno")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]))),
                    ft.DataCell(ft.Text(r[1] or "—")),
                    ft.DataCell(ft.Text(f"${r[2]:,.2f}")),
                ]) for r in rows
            ],
            **self.TABLE_STYLE,
        )


class VistaVentas(BaseVista):

    def build(self) -> ft.DataTable:
        rows = self._fetch("""
            SELECT v.id_venta, ec.nombre, p.id_proyecto,
                   c.nombre, v.precio, v.fecha_inicio, v.fecha_fin
            FROM venta v
            JOIN empresa_cliente ec ON ec.cif         = v.cif
            JOIN proyecto         p  ON p.id_proyecto  = v.id_proyecto
            JOIN consultor        c  ON c.cod_empleado = v.cod_empleado
            ORDER BY v.id_venta
        """)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID Venta")),
                ft.DataColumn(ft.Text("Empresa")),
                ft.DataColumn(ft.Text("Proy.")),
                ft.DataColumn(ft.Text("Consultor")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Inicio")),
                ft.DataColumn(ft.Text("Fin")),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(r[0]))),
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(str(r[2]))),
                    ft.DataCell(ft.Text(r[3])),
                    ft.DataCell(ft.Text(f"${r[4]:,.2f}")),
                    ft.DataCell(ft.Text(str(r[5]) if r[5] else "—")),
                    ft.DataCell(ft.Text(str(r[6]) if r[6] else "—")),
                ]) for r in rows
            ],
            **self.TABLE_STYLE,
        )


# ── Helpers de módulo (compatibilidad con main_screen.py existente) ───────────

def vista_consultores(conn, u):  return VistaConsultores(conn, u).build()
def vista_categorias(conn, u):   return VistaCategorias(conn, u).build()
def vista_empresas(conn, u):     return VistaEmpresas(conn, u).build()
def vista_proyectos(conn, u):    return VistaProyectos(conn, u).build()
def vista_ventas(conn, u):       return VistaVentas(conn, u).build()