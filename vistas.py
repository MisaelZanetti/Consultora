import flet as ft
from theme import C, T, S, R, divider

# ── Clase base ────────────────────────────────────────────────────────────────

class BaseVista:
    """Clase base para todas las vistas de tabla."""

    TABLE_STYLE = dict(
        border=ft.border.all(1, C.BORDER),
        heading_row_color=C.PRIMARY_BG,
        data_row_min_height=40,
        heading_row_height=44,
        divider_thickness=1,
        column_spacing=24,
    )

    def __init__(self, conn, usuario=None):
        self.conn    = conn
        self.usuario = usuario
        self._todos_los_rows: list = []
        self._tabla: ft.DataTable | None = None
        self._dialog: ft.AlertDialog | None = None

    # ── DB ───────────────────────────────────────────────────────────────────

    def _fetch(self, sql: str, params=()) -> list:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def _execute(self, sql: str, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        cursor.close()

    # ── Stubs para subclases ─────────────────────────────────────────────────

    def _hacer_filas(self, rows): raise NotImplementedError
    def _columnas(self):          raise NotImplementedError
    def _sql_all(self):           raise NotImplementedError
    def _abrir_alta(self):        pass
    def _abrir_editar(self, row): pass
    def _confirmar_baja(self, row): pass

    # ── Helpers de celda ─────────────────────────────────────────────────────

    @staticmethod
    def _col(text, numeric=False):
        return ft.DataColumn(
            ft.Text(text, size=T.SMALL, weight=ft.FontWeight.W_600, color=C.TEXT_SUB),
            numeric=numeric,
        )

    @staticmethod
    def _cell(text, mono=False):
        return ft.DataCell(ft.Text(
            str(text) if text is not None else "—",
            size=T.BODY, color=C.TEXT,
            font_family="monospace" if mono else None,
        ))

    @staticmethod
    def _cell_muted(text):
        return ft.DataCell(ft.Text(str(text) if text else "—", size=T.BODY, color=C.TEXT_SUB))

    # ── Helpers de UI ─────────────────────────────────────────────────────────

    @staticmethod
    def _field(label, value="", password=False, hint="", readonly=False):
        return ft.TextField(
            label=label, value=str(value) if value is not None else "",
            password=password, hint_text=hint, read_only=readonly,
            label_style=ft.TextStyle(size=T.SMALL, color=C.TEXT_SUB),
            text_style=ft.TextStyle(size=T.BODY, color=C.TEXT),
            border_color=C.BORDER, focused_border_color=C.PRIMARY,
            cursor_color=C.PRIMARY, bgcolor=C.BG, filled=True,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        )

    @staticmethod
    def _dropdown(label, options, value=None):
        return ft.Dropdown(
            label=label, value=value, options=options,
            label_style=ft.TextStyle(size=T.SMALL, color=C.TEXT_SUB),
            text_style=ft.TextStyle(size=T.BODY, color=C.TEXT),
            border_color=C.BORDER, focused_border_color=C.PRIMARY,
            bgcolor=C.BG, filled=True,
        )

    @staticmethod
    def _btn_accion(texto, icono, color, on_click):
        return ft.TextButton(
            content=ft.Row(
                controls=[ft.Icon(icono, size=16, color=color),
                           ft.Text(texto, size=T.SMALL, color=color)],
                spacing=4, tight=True,
            ),
            on_click=on_click,
            style=ft.ButtonStyle(overlay_color=C.BORDER),
        )

    def _btn_nuevo(self, label="Nuevo"):
        return ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.ADD, size=16, color=C.WHITE),
                           ft.Text(label, size=T.SMALL, color=C.WHITE)],
                spacing=4, tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor=C.PRIMARY, overlay_color=C.PRIMARY_DIM,
                shape=ft.RoundedRectangleBorder(radius=R.SM), elevation=0,
            ),
            height=36,
            on_click=lambda _: self._abrir_alta(),
        )

    def _acciones_celda(self, row):
        def _icon_btn(icon, color, tooltip, on_click):
            return ft.IconButton(
                icon=icon, icon_size=16, icon_color=color, tooltip=tooltip,
                style=ft.ButtonStyle(
                    overlay_color=C.PRIMARY_BG if color != C.ERROR else C.ERROR_BG,
                    shape=ft.RoundedRectangleBorder(radius=R.SM),
                ),
                on_click=on_click,
            )
        return ft.DataCell(ft.Row(controls=[
            _icon_btn(ft.Icons.EDIT_OUTLINED,   C.PRIMARY, "Editar",    lambda _, r=row: self._abrir_editar(r)),
            _icon_btn(ft.Icons.DELETE_OUTLINE,  C.ERROR,   "Eliminar",  lambda _, r=row: self._confirmar_baja(r)),
        ], spacing=2, tight=True))

    # ── Dialog ───────────────────────────────────────────────────────────────

    def _page(self):
        return self._tabla.page if self._tabla else None

    def _abrir_dialog(self, titulo, contenido, acciones):
        page = self._page()
        if not page:
            return
        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, size=T.TITLE, weight=ft.FontWeight.W_700, color=C.TEXT),
            content=ft.Container(content=contenido, bgcolor=C.SURFACE, width=440),
            actions=acciones,
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=C.SURFACE,
            shape=ft.RoundedRectangleBorder(radius=R.LG),
            title_padding=ft.padding.all(S.LG),
            content_padding=ft.padding.symmetric(horizontal=S.LG, vertical=S.SM),
            actions_padding=ft.padding.symmetric(horizontal=S.LG, vertical=S.MD),
        )
        page.overlay.append(self._dialog)
        self._dialog.open = True
        page.update()

    def _cerrar_dialog(self):
        if self._dialog and self._page():
            self._dialog.open = False
            self._page().update()
            self._dialog = None

    def _snack(self, mensaje, color=C.SUCCESS):
        page = self._page()
        if not page:
            return
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=C.WHITE), bgcolor=color, duration=2500,
        )
        page.snack_bar.open = True
        page.update()

    # ── Acciones de diálogo genéricas ─────────────────────────────────────────

    def _acciones_dialog(self, on_guardar, label_guardar="Guardar"):
        return [
            self._btn_accion("Cancelar", ft.Icons.CLOSE, C.TEXT_SUB, lambda _: self._cerrar_dialog()),
            self._btn_accion(label_guardar, ft.Icons.SAVE_OUTLINED, C.PRIMARY, on_guardar),
        ]

    def _dialog_confirmacion(self, titulo, texto_principal, texto_sec, on_eliminar):
        self._abrir_dialog(
            titulo,
            ft.Column(controls=[
                ft.Text(texto_principal, size=T.BODY, color=C.TEXT),
                ft.Text(texto_sec, size=T.SMALL, color=C.TEXT_SUB),
            ], spacing=S.SM, tight=True),
            [
                self._btn_accion("Cancelar", ft.Icons.CLOSE,          C.TEXT_SUB, lambda _: self._cerrar_dialog()),
                self._btn_accion("Eliminar", ft.Icons.DELETE_OUTLINE,  C.ERROR,    on_eliminar),
            ],
        )

    # ── Tabla ────────────────────────────────────────────────────────────────

    def _recargar(self):
        self._todos_los_rows = self._fetch(self._sql_all())
        self._actualizar_tabla(self._todos_los_rows)

    def _actualizar_tabla(self, rows):
        self._tabla.rows = self._hacer_filas(rows)
        if self._tabla.page:
            self._tabla.update()

    # ── Filtros ───────────────────────────────────────────────────────────────

    def _on_fetchall(self):
        self._actualizar_tabla(self._todos_los_rows)

    def _barra_filtros(self, *, dropdown_label, dropdown_opciones,
                       on_dropdown, on_fetchone, on_fetchall,
                       campo_busqueda_label="Buscar...", label_nuevo="Nuevo"):

        self._dd_label = ft.Text(
            dropdown_label if dropdown_label != "—" else "Filtrar",
            size=T.SMALL, color=C.TEXT, weight=ft.FontWeight.W_500,
        )

        def _hacer_item(opcion):
            def _h(_e, op=opcion):
                self._dd_label.value = op
                self._dd_label.update()
                on_dropdown(op)
            return ft.PopupMenuItem(content=ft.Text(opcion, size=T.BODY, color=C.TEXT), on_click=_h)

        items = [_hacer_item(o) for o in dropdown_opciones]

        dd_btn = ft.PopupMenuButton(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.FILTER_LIST_OUTLINED, size=15, color=C.TEXT_SUB),
                self._dd_label,
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=15, color=C.TEXT_SUB),
            ], spacing=4, tight=True),
            items=items or [ft.PopupMenuItem(content=ft.Text("Sin opciones", size=T.BODY))],
        )

        self._campo_busqueda = ft.TextField(
            label=campo_busqueda_label,
            label_style=ft.TextStyle(size=T.SMALL, color=C.TEXT_SUB),
            prefix_icon=ft.Icons.SEARCH, width=260, height=40,
            text_style=ft.TextStyle(size=T.BODY, color=C.TEXT),
            border_color=C.BORDER, focused_border_color=C.PRIMARY, cursor_color=C.PRIMARY,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            on_submit=lambda e: on_fetchone(e.control.value),
        )

        def _reset(_):
            self._dd_label.value = dropdown_label if dropdown_label != "—" else "Filtrar"
            self._campo_busqueda.value = ""
            on_fetchall()

        controles = []
        if items:
            controles.append(ft.Container(
                content=dd_btn, border=ft.border.all(1, C.BORDER),
                border_radius=R.SM, padding=ft.padding.symmetric(horizontal=S.SM, vertical=4),
                bgcolor=C.SURFACE,
            ))
        controles += [
            self._campo_busqueda,
            ft.IconButton(icon=ft.Icons.SEARCH, tooltip="Buscar", icon_color=C.PRIMARY, icon_size=18,
                          style=ft.ButtonStyle(bgcolor=C.PRIMARY_BG,
                                               shape=ft.RoundedRectangleBorder(radius=R.SM),
                                               overlay_color=C.BORDER),
                          on_click=lambda _: on_fetchone(self._campo_busqueda.value)),
            ft.IconButton(icon=ft.Icons.REFRESH_OUTLINED, tooltip="Mostrar todo",
                          icon_color=C.TEXT_SUB, icon_size=18,
                          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=R.SM),
                                               overlay_color=C.BORDER),
                          on_click=_reset),
            ft.Container(expand=True),
            self._btn_nuevo(label_nuevo),
        ]
        return ft.Row(controls=controles, spacing=S.SM, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _build_vista(self, barra_kwargs):
        self._todos_los_rows = self._fetch(self._sql_all())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todos_los_rows),
            **self.TABLE_STYLE,
        )
        barra = self._barra_filtros(
            on_fetchone=self._on_fetchone,
            on_fetchall=self._on_fetchall,
            **barra_kwargs,
        )
        return ft.Column(controls=[barra, self._tabla], spacing=S.MD)

    def build(self): raise NotImplementedError
    def __call__(self): return self.build()


# ── VistaConsultores ──────────────────────────────────────────────────────────

class VistaConsultores(BaseVista):

    _SQL = """
        SELECT c.cod_empleado, c.nombre, c.sueldo,
               cat.nombre AS categoria, j.nombre AS jefe,
               c.id_categoria, c.jefe AS cod_jefe
        FROM consultor c
        JOIN categoria cat ON cat.id_categoria = c.id_categoria
        LEFT JOIN consultor j ON j.cod_empleado = c.jefe
        {where}
        ORDER BY c.cod_empleado
    """

    def _columnas(self):
        return [self._col("CÓD."), self._col("NOMBRE"), self._col("SUELDO"),
                self._col("CATEGORÍA"), self._col("JEFE"), self._col("")]

    def _hacer_filas(self, rows):
        return [ft.DataRow(cells=[
            self._cell(r[0], mono=True), self._cell(r[1]),
            self._cell(f"${r[2]:,.2f}"), self._cell(r[3]),
            self._cell_muted(r[4]), self._acciones_celda(r),
        ]) for r in rows]

    def _sql_all(self): return self._SQL.format(where="")

    def _categorias(self):
        return [r[0] for r in self._fetch("SELECT nombre FROM categoria ORDER BY nombre")]

    def _categorias_dict(self):
        return {r[1]: r[0] for r in self._fetch("SELECT id_categoria, nombre FROM categoria ORDER BY nombre")}

    def _consultores_opciones(self):
        return self._fetch("SELECT cod_empleado, nombre FROM consultor ORDER BY nombre")

    def _on_dropdown(self, categoria):
        self._actualizar_tabla(self._fetch(self._SQL.format(where="WHERE cat.nombre = %s"), (categoria,)))

    def _on_fetchone(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._fetch(
                self._SQL.format(where="WHERE c.nombre LIKE %s OR c.cod_empleado LIKE %s"),
                (f"%{texto}%", f"%{texto}%"),
            ))

    def _form_fields(self, row=None):
        cats       = self._categorias_dict()
        consultores = self._consultores_opciones()
        cat_val    = next((n for n, i in cats.items() if i == (row[5] if row else None)), None)
        jefe_opts  = [ft.dropdown.Option("", text="— Sin jefe —")] + \
                     [ft.dropdown.Option(str(c[0]), text=f"{c[0]} – {c[1]}") for c in consultores]
        return (
            self._field("Código empleado", row[0] if row else "", readonly=row is not None),
            self._field("Nombre completo", row[1] if row else ""),
            self._field("Sueldo", str(row[2]) if row else ""),
            self._dropdown("Categoría", [ft.dropdown.Option(n) for n in cats], cat_val),
            self._dropdown("Jefe (opcional)", jefe_opts, str(row[6]) if row and row[6] else ""),
            cats,
        )

    def _guardar_consultor(self, fields, row=None):
        f_cod, f_nombre, f_sueldo, cat_dd, jefe_dd, cats = fields
        error = ft.Text("", color=C.ERROR, size=T.SMALL)

        def _on_save(_):
            cod    = (f_cod.value or "").strip()
            nombre = (f_nombre.value or "").strip()
            sueldo = (f_sueldo.value or "").strip()
            cat    = cat_dd.value
            jefe   = jefe_dd.value or None

            if (not row and not cod) or not nombre or not sueldo or not cat:
                error.value = "Todos los campos obligatorios deben completarse."
                error.update(); return
            try:
                sueldo_f = float(sueldo)
            except ValueError:
                error.value = "Sueldo debe ser un número."; error.update(); return

            id_cat   = cats[cat]
            jefe_val = jefe if jefe and jefe != "" else None
            try:
                if row:
                    self._execute(
                        "UPDATE consultor SET nombre=%s, sueldo=%s, id_categoria=%s, jefe=%s WHERE cod_empleado=%s",
                        (nombre, sueldo_f, id_cat, jefe_val, row[0]),
                    )
                    self._snack("Consultor actualizado.")
                else:
                    self._execute(
                        "INSERT INTO consultor (cod_empleado, nombre, sueldo, id_categoria, jefe) VALUES (%s,%s,%s,%s,%s)",
                        (cod, nombre, sueldo_f, id_cat, jefe_val),
                    )
                    self._snack("Consultor creado correctamente.")
                self._cerrar_dialog(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()

        return _on_save, error

    def _abrir_alta(self):
        fields = self._form_fields()
        f_cod, f_nombre, f_sueldo, cat_dd, jefe_dd, _ = fields
        on_save, error = self._guardar_consultor(fields)
        self._abrir_dialog("Nuevo consultor",
            ft.Column(controls=[f_cod, f_nombre, f_sueldo, cat_dd, jefe_dd, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _abrir_editar(self, row):
        fields = self._form_fields(row)
        f_cod, f_nombre, f_sueldo, cat_dd, jefe_dd, _ = fields
        on_save, error = self._guardar_consultor(fields, row)
        self._abrir_dialog(f"Editar consultor — {row[0]}",
            ft.Column(controls=[f_cod, f_nombre, f_sueldo, cat_dd, jefe_dd, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _confirmar_baja(self, row):
        def _eliminar(_):
            try:
                self._execute("DELETE FROM consultor WHERE cod_empleado=%s", (row[0],))
                self._cerrar_dialog(); self._recargar()
                self._snack("Consultor eliminado.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialog(); self._snack(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialog_confirmacion(
            "Confirmar eliminación",
            f"¿Eliminás al consultor {row[1]} ({row[0]})?",
            "Esta acción no se puede deshacer.", _eliminar,
        )

    def build(self):
        return self._build_vista(dict(
            dropdown_label="Categoría", dropdown_opciones=self._categorias(),
            on_dropdown=self._on_dropdown, campo_busqueda_label="Buscar por nombre o cód.",
            label_nuevo="Nuevo consultor",
        ))


# ── VistaCategorias ───────────────────────────────────────────────────────────

class VistaCategorias(BaseVista):

    _SQL = "SELECT id_categoria, nombre, salario_rec FROM categoria {where} ORDER BY id_categoria"

    def _columnas(self):
        return [self._col("ID"), self._col("NOMBRE"), self._col("SALARIO REC."), self._col("")]

    def _hacer_filas(self, rows):
        return [ft.DataRow(cells=[
            self._cell(r[0], mono=True), self._cell(r[1]),
            self._cell(f"${r[2]:,.2f}"), self._acciones_celda(r),
        ]) for r in rows]

    def _sql_all(self): return self._SQL.format(where="")
    def _on_dropdown(self, _): pass

    def _on_fetchone(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._fetch(self._SQL.format(where="WHERE nombre LIKE %s"), (f"%{texto}%",)))

    def _form_fields(self, row=None):
        return (self._field("Nombre", row[1] if row else ""),
                self._field("Salario recomendado", str(row[2]) if row else ""))

    def _guardar_categoria(self, f_nombre, f_salario, row=None):
        error = ft.Text("", color=C.ERROR, size=T.SMALL)
        def _on_save(_):
            nombre  = (f_nombre.value or "").strip()
            salario = (f_salario.value or "").strip()
            if not nombre or not salario:
                error.value = "Completá todos los campos."; error.update(); return
            try:
                if row:
                    self._execute("UPDATE categoria SET nombre=%s, salario_rec=%s WHERE id_categoria=%s",
                                  (nombre, float(salario), row[0]))
                    self._snack("Categoría actualizada.")
                else:
                    self._execute("INSERT INTO categoria (nombre, salario_rec) VALUES (%s, %s)",
                                  (nombre, float(salario)))
                    self._snack("Categoría creada.")
                self._cerrar_dialog(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _on_save, error

    def _abrir_alta(self):
        f_n, f_s = self._form_fields()
        on_save, error = self._guardar_categoria(f_n, f_s)
        self._abrir_dialog("Nueva categoría",
            ft.Column(controls=[f_n, f_s, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _abrir_editar(self, row):
        f_n, f_s = self._form_fields(row)
        on_save, error = self._guardar_categoria(f_n, f_s, row)
        self._abrir_dialog(f"Editar categoría — {row[1]}",
            ft.Column(controls=[f_n, f_s, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _confirmar_baja(self, row):
        def _eliminar(_):
            try:
                self._execute("DELETE FROM categoria WHERE id_categoria=%s", (row[0],))
                self._cerrar_dialog(); self._recargar()
                self._snack("Categoría eliminada.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialog(); self._snack(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialog_confirmacion("Confirmar eliminación",
            f"¿Eliminás la categoría «{row[1]}»?", "Esta acción no se puede deshacer.", _eliminar)

    def build(self):
        return self._build_vista(dict(
            dropdown_label="—", dropdown_opciones=[], on_dropdown=self._on_dropdown,
            campo_busqueda_label="Buscar por nombre", label_nuevo="Nueva categoría",
        ))


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
        return [self._col("CIF"), self._col("EMPRESA"), self._col("DIRECCIÓN"),
                self._col("TELÉFONOS"), self._col("")]

    def _hacer_filas(self, rows):
        return [ft.DataRow(cells=[
            self._cell(r[0], mono=True), self._cell(r[1]), self._cell(r[2]),
            self._cell_muted(r[3]), self._acciones_celda(r),
        ]) for r in rows]

    def _sql_all(self): return self._SQL.format(where="")
    def _on_dropdown(self, _): pass

    def _on_fetchone(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._fetch(
                self._SQL.format(where="WHERE ec.nombre LIKE %s OR ec.cif LIKE %s"),
                (f"%{texto}%", f"%{texto}%"),
            ))

    def _form_fields(self, row=None):
        return (
            self._field("CIF", row[0] if row else "", readonly=row is not None),
            self._field("Nombre empresa", row[1] if row else ""),
            self._field("Dirección", row[2] if row else ""),
            self._field("Teléfono(s)", row[3].replace(" / ", ", ") if row and row[3] else "", hint="Separados por coma"),
        )

    def _guardar_telefonos(self, cif, telefonos_raw):
        self._execute("DELETE FROM telefono_cliente WHERE cif=%s", (cif,))
        for tel in telefonos_raw.split(","):
            if t := tel.strip():
                self._execute("INSERT INTO telefono_cliente (cif, telefono) VALUES (%s,%s)", (cif, t))

    def _guardar_empresa(self, f_cif, f_nombre, f_dir, f_tel, row=None):
        error = ft.Text("", color=C.ERROR, size=T.SMALL)
        def _on_save(_):
            cif    = (f_cif.value or "").strip()
            nombre = (f_nombre.value or "").strip()
            dir_   = (f_dir.value or "").strip()
            if not nombre or (not row and not cif):
                error.value = "CIF y nombre son obligatorios."; error.update(); return
            try:
                if row:
                    self._execute("UPDATE empresa_cliente SET nombre=%s, direccion=%s WHERE cif=%s",
                                  (nombre, dir_, row[0]))
                    self._guardar_telefonos(row[0], f_tel.value or "")
                    self._snack("Empresa actualizada.")
                else:
                    self._execute("INSERT INTO empresa_cliente (cif, nombre, direccion) VALUES (%s,%s,%s)",
                                  (cif, nombre, dir_))
                    self._guardar_telefonos(cif, f_tel.value or "")
                    self._snack("Empresa creada.")
                self._cerrar_dialog(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _on_save, error

    def _abrir_alta(self):
        f_c, f_n, f_d, f_t = self._form_fields()
        on_save, error = self._guardar_empresa(f_c, f_n, f_d, f_t)
        self._abrir_dialog("Nueva empresa cliente",
            ft.Column(controls=[f_c, f_n, f_d, f_t, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _abrir_editar(self, row):
        f_c, f_n, f_d, f_t = self._form_fields(row)
        on_save, error = self._guardar_empresa(f_c, f_n, f_d, f_t, row)
        self._abrir_dialog(f"Editar empresa — {row[0]}",
            ft.Column(controls=[f_c, f_n, f_d, f_t, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _confirmar_baja(self, row):
        def _eliminar(_):
            try:
                self._execute("DELETE FROM telefono_cliente WHERE cif=%s", (row[0],))
                self._execute("DELETE FROM empresa_cliente WHERE cif=%s", (row[0],))
                self._cerrar_dialog(); self._recargar()
                self._snack("Empresa eliminada.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialog(); self._snack(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialog_confirmacion("Confirmar eliminación",
            f"¿Eliminás la empresa «{row[1]}» (CIF: {row[0]})?",
            "Se eliminarán también sus teléfonos.", _eliminar)

    def build(self):
        return self._build_vista(dict(
            dropdown_label="—", dropdown_opciones=[], on_dropdown=self._on_dropdown,
            campo_busqueda_label="Buscar por nombre o CIF", label_nuevo="Nueva empresa",
        ))


# ── VistaProyectos ────────────────────────────────────────────────────────────

class VistaProyectos(BaseVista):

    _SQL = "SELECT id_proyecto, descripcion, coste FROM proyecto {where} ORDER BY id_proyecto"

    def _columnas(self):
        return [self._col("ID"), self._col("DESCRIPCIÓN"), self._col("COSTE INTERNO"),
                self._col("EQUIPO"), self._col("")]

    def _contar_equipo(self, id_proyecto):
        rows = self._fetch("SELECT COUNT(*) FROM consultor_proyecto WHERE id_proyecto = %s", (id_proyecto,))
        return rows[0][0] if rows else 0

    def _chip_equipo(self, cant):
        return ft.Container(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=13, color=C.PRIMARY),
                ft.Text(str(cant), size=T.SMALL, color=C.PRIMARY, weight=ft.FontWeight.W_600),
            ], spacing=4, tight=True),
            bgcolor=C.PRIMARY_BG, border_radius=R.SM,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

    def _hacer_filas(self, rows):
        return [ft.DataRow(cells=[
            self._cell(r[0], mono=True), self._cell(r[1]),
            self._cell(f"${r[2]:,.2f}"),
            ft.DataCell(self._chip_equipo(self._contar_equipo(r[0]))),
            self._acciones_celda_proyecto(r),
        ]) for r in rows]

    def _acciones_celda_proyecto(self, row):
        def _ibtn(icon, color, tooltip, handler):
            return ft.IconButton(
                icon=icon, icon_size=16, icon_color=color, tooltip=tooltip,
                style=ft.ButtonStyle(overlay_color=C.PRIMARY_BG if color != C.ERROR else C.ERROR_BG,
                                     shape=ft.RoundedRectangleBorder(radius=R.SM)),
                on_click=lambda _, r=row: handler(r),
            )
        return ft.DataCell(ft.Row(controls=[
            _ibtn(ft.Icons.GROUP_OUTLINED,   C.SUCCESS, "Gestionar equipo",    self._abrir_equipo),
            _ibtn(ft.Icons.BUSINESS_OUTLINED, C.PRIMARY, "Empresas clientes",  self._abrir_empresas),
            _ibtn(ft.Icons.EDIT_OUTLINED,    C.PRIMARY, "Editar",              self._abrir_editar),
            _ibtn(ft.Icons.DELETE_OUTLINE,   C.ERROR,   "Eliminar",            self._confirmar_baja),
        ], spacing=2, tight=True))

    def _sql_all(self): return self._SQL.format(where="")
    def _on_dropdown(self, _): pass

    def _on_fetchone(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._fetch(
                self._SQL.format(where="WHERE descripcion LIKE %s OR id_proyecto LIKE %s"),
                (f"%{texto}%", f"%{texto}%"),
            ))

    def _form_fields(self, row=None):
        return (self._field("Descripción", row[1] if row else ""),
                self._field("Coste interno", str(row[2]) if row else ""))

    def _guardar_proyecto(self, f_desc, f_coste, row=None):
        error = ft.Text("", color=C.ERROR, size=T.SMALL)
        def _on_save(_):
            desc  = (f_desc.value or "").strip()
            coste = (f_coste.value or "").strip()
            if not desc or not coste:
                error.value = "Completá todos los campos."; error.update(); return
            try:
                if row:
                    self._execute("UPDATE proyecto SET descripcion=%s, coste=%s WHERE id_proyecto=%s",
                                  (desc, float(coste), row[0]))
                    self._snack("Proyecto actualizado.")
                else:
                    self._execute("INSERT INTO proyecto (descripcion, coste) VALUES (%s,%s)",
                                  (desc, float(coste)))
                    self._snack("Proyecto creado.")
                self._cerrar_dialog(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _on_save, error

    def _abrir_alta(self):
        f_d, f_c = self._form_fields()
        on_save, error = self._guardar_proyecto(f_d, f_c)
        self._abrir_dialog("Nuevo proyecto",
            ft.Column(controls=[f_d, f_c, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _abrir_editar(self, row):
        f_d, f_c = self._form_fields(row)
        on_save, error = self._guardar_proyecto(f_d, f_c, row)
        self._abrir_dialog(f"Editar proyecto — {row[0]}",
            ft.Column(controls=[f_d, f_c, error], spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _confirmar_baja(self, row):
        def _eliminar(_):
            try:
                self._execute("DELETE FROM consultor_proyecto WHERE id_proyecto=%s", (row[0],))
                self._execute("DELETE FROM proyecto WHERE id_proyecto=%s", (row[0],))
                self._cerrar_dialog(); self._recargar()
                self._snack("Proyecto eliminado.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialog(); self._snack(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialog_confirmacion("Confirmar eliminación",
            f"¿Eliminás el proyecto #{row[0]}?", "Esta acción no se puede deshacer.", _eliminar)

    # ── Panel de relaciones (equipo / empresas) ───────────────────────────────

    def _panel_relacion(self, id_entidad, titulo_dialog, label_lista, label_vacio,
                        label_dd, sql_todos, sql_asignados, icon_fila,
                        sql_insertar, sql_quitar, pk_col, error_sel):
        """Panel genérico para gestionar relaciones M:N en un diálogo."""
        lista   = ft.Column(spacing=S.XS, tight=True)
        error   = ft.Text("", color=C.ERROR, size=T.SMALL)
        todos   = self._fetch(sql_todos)
        dd      = self._dropdown(label_dd,
                                 [ft.dropdown.Option(str(r[0]), text=str(r[1])) for r in todos])

        def _page(): return self._tabla.page if self._tabla else None

        def _refrescar():
            asignados = self._fetch(sql_asignados, (id_entidad,))
            lista.controls.clear()
            if not asignados:
                lista.controls.append(ft.Text(label_vacio, size=T.SMALL, color=C.TEXT_SUB))
            else:
                for a in asignados:
                    pk, nombre, subtitulo = a[0], a[1], a[2] if len(a) > 2 else ""

                    def _quitar(_, p=pk):
                        try:
                            self._execute(sql_quitar, (id_entidad, p))
                            error.value = ""
                            _refrescar()
                            self._todos_los_rows = self._fetch(self._sql_all())
                            self._tabla.rows = self._hacer_filas(self._todos_los_rows)
                            if pg := _page(): pg.update()
                        except Exception as ex:
                            error.value = f"Error: {ex}"
                            if pg := _page(): pg.update()

                    lista.controls.append(ft.Container(
                        content=ft.Row(controls=[
                            ft.Container(content=ft.Icon(icon_fila, size=14, color=C.PRIMARY),
                                         bgcolor=C.PRIMARY_BG, border_radius=R.SM,
                                         padding=ft.padding.all(4)),
                            ft.Column(controls=[
                                ft.Text(nombre, size=T.BODY, color=C.TEXT, weight=ft.FontWeight.W_500),
                                ft.Text(subtitulo, size=T.SMALL, color=C.TEXT_SUB),
                            ], spacing=0, tight=True, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                icon_size=16, icon_color=C.ERROR, tooltip="Quitar",
                                style=ft.ButtonStyle(overlay_color=C.ERROR_BG,
                                                     shape=ft.RoundedRectangleBorder(radius=R.SM)),
                                on_click=_quitar,
                            ),
                        ], spacing=S.SM, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=C.BG, border=ft.border.all(1, C.BORDER),
                        border_radius=R.MD,
                        padding=ft.padding.symmetric(horizontal=S.SM, vertical=S.XS),
                    ))
            if pg := _page(): pg.update()

        def _agregar(_):
            val = dd.value
            if not val:
                error.value = error_sel
                if pg := _page(): pg.update()
                return
            try:
                self._execute(sql_insertar, (id_entidad, int(val) if val.isdigit() else val))
                dd.value = None; error.value = ""
                _refrescar()
                self._todos_los_rows = self._fetch(self._sql_all())
                self._tabla.rows = self._hacer_filas(self._todos_los_rows)
                if pg := _page(): pg.update()
            except Exception as ex:
                error.value = f"Error: {ex}"
                if pg := _page(): pg.update()

        _refrescar()
        contenido = ft.Column(controls=[
            ft.Text(label_lista, size=T.SMALL, color=C.TEXT_SUB, weight=ft.FontWeight.W_600),
            ft.Container(content=lista, bgcolor=C.SURFACE, border_radius=R.MD,
                         padding=S.SM, border=ft.border.all(1, C.BORDER)),
            dd,
            ft.Row(controls=[
                ft.Container(expand=True),
                self._btn_accion("Agregar", ft.Icons.ADD, C.PRIMARY, _agregar),
            ]),
            error,
        ], spacing=S.SM, tight=True)

        self._abrir_dialog(titulo_dialog, contenido,
                           [self._btn_accion("Cerrar", ft.Icons.CLOSE, C.TEXT_SUB,
                                             lambda _: self._cerrar_dialog())])

    def _abrir_equipo(self, row):
        self._panel_relacion(
            id_entidad=row[0],
            titulo_dialog=f"Equipo — Proyecto #{row[0]}",
            label_lista="Consultores asignados",
            label_vacio="Sin consultores asignados.",
            label_dd="Agregar consultor",
            sql_todos="SELECT cod_empleado, nombre FROM consultor ORDER BY nombre",
            sql_asignados="""
                SELECT c.cod_empleado, c.nombre, cat.nombre
                FROM consultor_proyecto cp
                JOIN consultor c   ON c.cod_empleado = cp.cod_empleado
                JOIN categoria cat ON cat.id_categoria = c.id_categoria
                WHERE cp.id_proyecto = %s ORDER BY c.nombre
            """,
            icon_fila=ft.Icons.PERSON_OUTLINE,
            sql_insertar="INSERT IGNORE INTO consultor_proyecto (id_proyecto, cod_empleado) VALUES (%s,%s)",
            sql_quitar="DELETE FROM consultor_proyecto WHERE id_proyecto=%s AND cod_empleado=%s",
            pk_col="cod_empleado",
            error_sel="Seleccioná un consultor.",
        )

    def _abrir_empresas(self, row):
        self._panel_relacion(
            id_entidad=row[0],
            titulo_dialog=f"Empresas clientes — Proyecto #{row[0]}",
            label_lista="Empresas asignadas",
            label_vacio="Sin empresas asignadas.",
            label_dd="Agregar empresa cliente",
            sql_todos="SELECT cif, nombre FROM empresa_cliente ORDER BY nombre",
            sql_asignados="""
                SELECT ec.cif, ec.nombre, ec.direccion
                FROM proyecto_empresa pe
                JOIN empresa_cliente ec ON ec.cif = pe.cif
                WHERE pe.id_proyecto = %s ORDER BY ec.nombre
            """,
            icon_fila=ft.Icons.BUSINESS_OUTLINED,
            sql_insertar="INSERT IGNORE INTO proyecto_empresa (id_proyecto, cif) VALUES (%s,%s)",
            sql_quitar="DELETE FROM proyecto_empresa WHERE id_proyecto=%s AND cif=%s",
            pk_col="cif",
            error_sel="Seleccioná una empresa.",
        )

    def build(self):
        return self._build_vista(dict(
            dropdown_label="—", dropdown_opciones=[], on_dropdown=self._on_dropdown,
            campo_busqueda_label="Buscar por descripción o ID", label_nuevo="Nuevo proyecto",
        ))


# ── VistaVentas ───────────────────────────────────────────────────────────────

class VistaVentas(BaseVista):

    _SQL = """
        SELECT v.id_venta, ec.nombre, p.id_proyecto,
               c.nombre, v.precio, v.fecha_inicio, v.fecha_fin,
               v.cif, v.cod_empleado
        FROM venta v
        JOIN empresa_cliente ec ON ec.cif         = v.cif
        JOIN proyecto         p  ON p.id_proyecto  = v.id_proyecto
        JOIN consultor        c  ON c.cod_empleado = v.cod_empleado
        {where}
        ORDER BY v.id_venta
    """

    def _columnas(self):
        return [self._col("ID"), self._col("EMPRESA"), self._col("PROY."),
                self._col("CONSULTOR"), self._col("PRECIO"),
                self._col("INICIO"), self._col("FIN"), self._col("")]

    def _hacer_filas(self, rows):
        return [ft.DataRow(cells=[
            self._cell(r[0], mono=True), self._cell(r[1]),
            self._cell(r[2], mono=True), self._cell(r[3]),
            self._cell(f"${r[4]:,.2f}"),
            self._cell_muted(r[5]), self._cell_muted(r[6]),
            self._acciones_celda(r),
        ]) for r in rows]

    def _sql_all(self): return self._SQL.format(where="")

    def _empresas(self):
        return [r[0] for r in self._fetch("SELECT nombre FROM empresa_cliente ORDER BY nombre")]

    def _empresas_dict(self):
        return {r[1]: r[0] for r in self._fetch("SELECT cif, nombre FROM empresa_cliente ORDER BY nombre")}

    def _on_dropdown(self, empresa):
        self._actualizar_tabla(self._fetch(self._SQL.format(where="WHERE ec.nombre = %s"), (empresa,)))

    def _on_fetchone(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._fetch(
                self._SQL.format(where="WHERE v.id_venta LIKE %s OR c.nombre LIKE %s OR ec.nombre LIKE %s"),
                (f"%{texto}%", f"%{texto}%", f"%{texto}%"),
            ))

    def _form_fields(self, row=None):
        empresas  = self._empresas_dict()
        proyectos = self._fetch("SELECT id_proyecto, descripcion FROM proyecto ORDER BY id_proyecto")
        consults  = self._fetch("SELECT cod_empleado, nombre FROM consultor ORDER BY nombre")
        emp_val   = next((n for n, c in empresas.items() if c == (row[7] if row else None)), None)
        return (
            self._dropdown("Empresa cliente", [ft.dropdown.Option(n) for n in empresas], emp_val),
            self._dropdown("Proyecto",
                [ft.dropdown.Option(str(p[0]), text=f"{p[0]} – {p[1][:40]}") for p in proyectos],
                str(row[2]) if row else None),
            self._dropdown("Consultor",
                [ft.dropdown.Option(str(c[0]), text=f"{c[0]} – {c[1]}") for c in consults],
                str(row[8]) if row else None),
            self._field("Precio de venta", str(row[4]) if row else ""),
            self._field("Fecha inicio (AAAA-MM-DD)", str(row[5]) if row else "", hint="2024-01-15"),
            self._field("Fecha fin (AAAA-MM-DD)",    str(row[6]) if row else "", hint="2024-12-31"),
            empresas,
        )

    def _guardar_venta(self, fields, row=None):
        emp_dd, proy_dd, cons_dd, f_precio, f_inicio, f_fin, empresas = fields
        error = ft.Text("", color=C.ERROR, size=T.SMALL)

        def _sync(cif, proy):
            self._execute("INSERT IGNORE INTO consultor_proyecto (cod_empleado, id_proyecto) VALUES (%s,%s)",
                          (cons_dd.value, int(proy)))
            self._execute("INSERT IGNORE INTO proyecto_empresa (id_proyecto, cif) VALUES (%s,%s)",
                          (int(proy), cif))

        def _on_save(_):
            emp    = emp_dd.value
            proy   = proy_dd.value
            cons   = cons_dd.value
            precio = (f_precio.value or "").strip()
            inicio = (f_inicio.value or "").strip()
            fin    = (f_fin.value or "").strip()
            if not all([emp, proy, cons, precio, inicio, fin]):
                error.value = "Todos los campos son obligatorios."; error.update(); return
            try:
                cif = empresas[emp]
                if row:
                    self._execute(
                        "UPDATE venta SET cif=%s, id_proyecto=%s, cod_empleado=%s, precio=%s, fecha_inicio=%s, fecha_fin=%s WHERE id_venta=%s",
                        (cif, int(proy), cons, float(precio), inicio, fin, row[0]),
                    )
                    self._snack("Venta actualizada.")
                else:
                    self._execute(
                        "INSERT INTO venta (cif, id_proyecto, cod_empleado, precio, fecha_inicio, fecha_fin) VALUES (%s,%s,%s,%s,%s,%s)",
                        (cif, int(proy), cons, float(precio), inicio, fin),
                    )
                    self._snack("Venta registrada.")
                _sync(cif, proy)
                self._cerrar_dialog(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _on_save, error

    def _abrir_alta(self):
        fields = self._form_fields()
        emp_dd, proy_dd, cons_dd, f_precio, f_inicio, f_fin, _ = fields
        on_save, error = self._guardar_venta(fields)
        self._abrir_dialog("Nueva venta",
            ft.Column(controls=[emp_dd, proy_dd, cons_dd, f_precio, f_inicio, f_fin, error],
                      spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _abrir_editar(self, row):
        fields = self._form_fields(row)
        emp_dd, proy_dd, cons_dd, f_precio, f_inicio, f_fin, _ = fields
        on_save, error = self._guardar_venta(fields, row)
        self._abrir_dialog(f"Editar venta — #{row[0]}",
            ft.Column(controls=[emp_dd, proy_dd, cons_dd, f_precio, f_inicio, f_fin, error],
                      spacing=S.MD, tight=True),
            self._acciones_dialog(on_save))

    def _confirmar_baja(self, row):
        def _eliminar(_):
            try:
                self._execute("DELETE FROM venta WHERE id_venta=%s", (row[0],))
                self._cerrar_dialog(); self._recargar()
                self._snack("Venta eliminada.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialog(); self._snack(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialog_confirmacion("Confirmar eliminación",
            f"¿Eliminás la venta #{row[0]} ({row[1]})?",
            "Esta acción no se puede deshacer.", _eliminar)

    def build(self):
        return self._build_vista(dict(
            dropdown_label="Empresa", dropdown_opciones=self._empresas(),
            on_dropdown=self._on_dropdown,
            campo_busqueda_label="Buscar por ID, consultor o empresa",
            label_nuevo="Nueva venta",
        ))


# ── Helpers de módulo ─────────────────────────────────────────────────────────

def vista_consultores(conn, u): return VistaConsultores(conn, u).build()
def vista_categorias(conn, u):  return VistaCategorias(conn, u).build()
def vista_empresas(conn, u):    return VistaEmpresas(conn, u).build()
def vista_proyectos(conn, u):   return VistaProyectos(conn, u).build()
def vista_ventas(conn, u):      return VistaVentas(conn, u).build()