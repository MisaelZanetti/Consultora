import flet as ft
from tema import C, T, E, R, divisor


class VistaBase:
    ESTILO_TABLA = dict(
        border=ft.border.all(1, C.BORDE),
        heading_row_color=C.PRIMARIO_FONDO,
        data_row_min_height=40,
        heading_row_height=44,
        divider_thickness=1,
        column_spacing=24,
    )

    def __init__(self, conn, usuario=None):
        self.conn    = conn
        self.usuario = usuario
        self._todas_las_filas: list = []
        self._tabla: ft.DataTable | None = None
        self._dialogo: ft.AlertDialog | None = None

    def _consultar(self, sql: str, params=()) -> list:
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        filas = cursor.fetchall()
        cursor.close()
        return filas

    def _ejecutar(self, sql: str, params=()):
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        self.conn.commit()
        cursor.close()

    def _hacer_filas(self, filas): raise NotImplementedError
    def _columnas(self):           raise NotImplementedError
    def _sql_todas(self):          raise NotImplementedError
    def _abrir_alta(self):         pass
    def _abrir_editar(self, fila): pass
    def _confirmar_baja(self, fila): pass

    @staticmethod
    def _col(texto, numerico=False):
        return ft.DataColumn(
            ft.Text(texto, size=T.PEQUEÑO, weight=ft.FontWeight.W_600, color=C.TEXTO_SEC),
            numeric=numerico,
        )

    @staticmethod
    def _celda(texto, mono=False):
        return ft.DataCell(ft.Text(
            str(texto) if texto is not None else "—",
            size=T.CUERPO, color=C.TEXTO,
            font_family="monospace" if mono else None,
        ))

    @staticmethod
    def _celda_atenuada(texto):
        return ft.DataCell(ft.Text(str(texto) if texto else "—", size=T.CUERPO, color=C.TEXTO_SEC))

    @staticmethod
    def _campo(etiqueta, valor="", contrasena=False, pista="", solo_lectura=False):
        return ft.TextField(
            label=etiqueta, value=str(valor) if valor is not None else "",
            password=contrasena, hint_text=pista, read_only=solo_lectura,
            label_style=ft.TextStyle(size=T.PEQUEÑO, color=C.TEXTO_SEC),
            text_style=ft.TextStyle(size=T.CUERPO, color=C.TEXTO),
            border_color=C.BORDE, focused_border_color=C.PRIMARIO,
            cursor_color=C.PRIMARIO, bgcolor=C.FONDO, filled=True,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=10),
        )

    @staticmethod
    def _desplegable(etiqueta, opciones, valor=None):
        return ft.Dropdown(
            label=etiqueta, value=valor, options=opciones,
            label_style=ft.TextStyle(size=T.PEQUEÑO, color=C.TEXTO_SEC),
            text_style=ft.TextStyle(size=T.CUERPO, color=C.TEXTO),
            border_color=C.BORDE, focused_border_color=C.PRIMARIO,
            bgcolor=C.FONDO, filled=True,
        )

    @staticmethod
    def _btn_accion(texto, icono, color, al_hacer_click):
        return ft.TextButton(
            content=ft.Row(
                controls=[ft.Icon(icono, size=16, color=color),
                           ft.Text(texto, size=T.PEQUEÑO, color=color)],
                spacing=4, tight=True,
            ),
            on_click=al_hacer_click,
            style=ft.ButtonStyle(overlay_color=C.BORDE),
        )

    def _btn_nuevo(self, etiqueta="Nuevo"):
        return ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.ADD, size=16, color=C.BLANCO),
                           ft.Text(etiqueta, size=T.PEQUEÑO, color=C.BLANCO)],
                spacing=4, tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor=C.PRIMARIO, overlay_color=C.PRIMARIO_OSC,
                shape=ft.RoundedRectangleBorder(radius=R.CH), elevation=0,
            ),
            height=36,
            on_click=lambda _: self._abrir_alta(),
        )

    def _acciones_celda(self, fila):
        def _btn_icono(icono, color, tooltip, al_hacer_click):
            return ft.IconButton(
                icon=icono, icon_size=16, icon_color=color, tooltip=tooltip,
                style=ft.ButtonStyle(
                    overlay_color=C.PRIMARIO_FONDO if color != C.ERROR else C.ERROR_FONDO,
                    shape=ft.RoundedRectangleBorder(radius=R.CH),
                ),
                on_click=al_hacer_click,
            )
        return ft.DataCell(ft.Row(controls=[
            _btn_icono(ft.Icons.EDIT_OUTLINED,  C.PRIMARIO, "Editar",   lambda _, f=fila: self._abrir_editar(f)),
            _btn_icono(ft.Icons.DELETE_OUTLINE, C.ERROR,    "Eliminar", lambda _, f=fila: self._confirmar_baja(f)),
        ], spacing=2, tight=True))

    def _pagina(self):
        return self._tabla.page if self._tabla else None

    def _abrir_dialogo(self, titulo, contenido, acciones):
        pagina = self._pagina()
        if not pagina:
            return
        self._dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text(titulo, size=T.TITULO, weight=ft.FontWeight.W_700, color=C.TEXTO),
            content=ft.Container(content=contenido, bgcolor=C.SUPERFICIE, width=440),
            actions=acciones,
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=C.SUPERFICIE,
            shape=ft.RoundedRectangleBorder(radius=R.GD),
            title_padding=ft.padding.all(E.GD),
            content_padding=ft.padding.symmetric(horizontal=E.GD, vertical=E.CH),
            actions_padding=ft.padding.symmetric(horizontal=E.GD, vertical=E.MD),
        )
        pagina.overlay.append(self._dialogo)
        self._dialogo.open = True
        pagina.update()

    def _cerrar_dialogo(self):
        if self._dialogo and self._pagina():
            self._dialogo.open = False
            self._pagina().update()
            self._dialogo = None

    def _notificacion(self, mensaje, color=C.EXITO):
        pagina = self._pagina()
        if not pagina:
            return
        pagina.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=C.BLANCO), bgcolor=color, duration=2500,
        )
        pagina.snack_bar.open = True
        pagina.update()

    def _acciones_dialogo(self, al_guardar, etiqueta_guardar="Guardar"):
        return [
            self._btn_accion("Cancelar", ft.Icons.CLOSE, C.TEXTO_SEC, lambda _: self._cerrar_dialogo()),
            self._btn_accion(etiqueta_guardar, ft.Icons.SAVE_OUTLINED, C.PRIMARIO, al_guardar),
        ]

    def _dialogo_confirmacion(self, titulo, texto_principal, texto_sec, al_eliminar):
        self._abrir_dialogo(
            titulo,
            ft.Column(controls=[
                ft.Text(texto_principal, size=T.CUERPO, color=C.TEXTO),
                ft.Text(texto_sec, size=T.PEQUEÑO, color=C.TEXTO_SEC),
            ], spacing=E.CH, tight=True),
            [
                self._btn_accion("Cancelar", ft.Icons.CLOSE,         C.TEXTO_SEC, lambda _: self._cerrar_dialogo()),
                self._btn_accion("Eliminar", ft.Icons.DELETE_OUTLINE, C.ERROR,    al_eliminar),
            ],
        )

    def _recargar(self):
        self._todas_las_filas = self._consultar(self._sql_todas())
        self._actualizar_tabla(self._todas_las_filas)

    def _actualizar_tabla(self, filas):
        self._tabla.rows = self._hacer_filas(filas)
        if self._tabla.page:
            self._tabla.update()

    def _al_mostrar_todos(self):
        self._actualizar_tabla(self._todas_las_filas)

    def _barra_filtros(self, *, etiqueta_dd, opciones_dd,
                       al_seleccionar_dd, al_buscar_uno, al_mostrar_todos,
                       etiqueta_busqueda="Buscar...", etiqueta_nuevo="Nuevo"):

        self._texto_dd = ft.Text(
            etiqueta_dd if etiqueta_dd != "—" else "Filtrar",
            size=T.PEQUEÑO, color=C.TEXTO, weight=ft.FontWeight.W_500,
        )

        def _hacer_elemento(opcion):
            def _manejador(_e, op=opcion):
                self._texto_dd.value = op
                self._texto_dd.update()
                al_seleccionar_dd(op)
            return ft.PopupMenuItem(content=ft.Text(opcion, size=T.CUERPO, color=C.TEXTO), on_click=_manejador)

        elementos = [_hacer_elemento(o) for o in opciones_dd]

        btn_dd = ft.PopupMenuButton(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.FILTER_LIST_OUTLINED, size=15, color=C.TEXTO_SEC),
                self._texto_dd,
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=15, color=C.TEXTO_SEC),
            ], spacing=4, tight=True),
            items=elementos or [ft.PopupMenuItem(content=ft.Text("Sin opciones", size=T.CUERPO))],
        )

        self._campo_busqueda = ft.TextField(
            label=etiqueta_busqueda,
            label_style=ft.TextStyle(size=T.PEQUEÑO, color=C.TEXTO_SEC),
            prefix_icon=ft.Icons.SEARCH, width=260, height=40,
            text_style=ft.TextStyle(size=T.CUERPO, color=C.TEXTO),
            border_color=C.BORDE, focused_border_color=C.PRIMARIO, cursor_color=C.PRIMARIO,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            on_submit=lambda e: al_buscar_uno(e.control.value),
        )

        def _reiniciar(_):
            self._texto_dd.value = etiqueta_dd if etiqueta_dd != "—" else "Filtrar"
            self._campo_busqueda.value = ""
            al_mostrar_todos()

        controles = []
        if elementos:
            controles.append(ft.Container(
                content=btn_dd, border=ft.border.all(1, C.BORDE),
                border_radius=R.CH, padding=ft.padding.symmetric(horizontal=E.CH, vertical=4),
                bgcolor=C.SUPERFICIE,
            ))
        controles += [
            self._campo_busqueda,
            ft.IconButton(icon=ft.Icons.SEARCH, tooltip="Buscar", icon_color=C.PRIMARIO, icon_size=18,
                          style=ft.ButtonStyle(bgcolor=C.PRIMARIO_FONDO,
                                               shape=ft.RoundedRectangleBorder(radius=R.CH),
                                               overlay_color=C.BORDE),
                          on_click=lambda _: al_buscar_uno(self._campo_busqueda.value)),
            ft.IconButton(icon=ft.Icons.REFRESH_OUTLINED, tooltip="Mostrar todo",
                          icon_color=C.TEXTO_SEC, icon_size=18,
                          style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=R.CH),
                                               overlay_color=C.BORDE),
                          on_click=_reiniciar),
            ft.Container(expand=True),
            self._btn_nuevo(etiqueta_nuevo),
        ]
        return ft.Row(controls=controles, spacing=E.CH, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _construir_vista(self, kwargs_barra):
        self._todas_las_filas = self._consultar(self._sql_todas())
        self._tabla = ft.DataTable(
            columns=self._columnas(),
            rows=self._hacer_filas(self._todas_las_filas),
            **self.ESTILO_TABLA,
        )
        barra = self._barra_filtros(
            al_buscar_uno=self._al_buscar_uno,
            al_mostrar_todos=self._al_mostrar_todos,
            **kwargs_barra,
        )
        return ft.Column(controls=[barra, self._tabla], spacing=E.MD)

    def build(self): raise NotImplementedError
    def __call__(self): return self.build()


class VistaConsultores(VistaBase):

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

    def _hacer_filas(self, filas):
        return [ft.DataRow(cells=[
            self._celda(f[0], mono=True), self._celda(f[1]),
            self._celda(f"${f[2]:,.2f}"), self._celda(f[3]),
            self._celda_atenuada(f[4]), self._acciones_celda(f),
        ]) for f in filas]

    def _sql_todas(self): return self._SQL.format(where="")

    def _categorias(self):
        return [f[0] for f in self._consultar("SELECT nombre FROM categoria ORDER BY nombre")]

    def _categorias_dict(self):
        return {f[1]: f[0] for f in self._consultar("SELECT id_categoria, nombre FROM categoria ORDER BY nombre")}

    def _opciones_consultores(self):
        return self._consultar("SELECT cod_empleado, nombre FROM consultor ORDER BY nombre")

    def _al_seleccionar_dd(self, categoria):
        self._actualizar_tabla(self._consultar(self._SQL.format(where="WHERE cat.nombre = %s"), (categoria,)))

    def _al_buscar_uno(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._consultar(
                self._SQL.format(where="WHERE c.nombre LIKE %s OR c.cod_empleado LIKE %s"),
                (f"%{texto}%", f"%{texto}%"),
            ))

    def _campos_formulario(self, fila=None):
        cats        = self._categorias_dict()
        consultores = self._opciones_consultores()
        val_cat     = next((n for n, i in cats.items() if i == (fila[5] if fila else None)), None)
        ops_jefe    = [ft.dropdown.Option("", text="— Sin jefe —")] + \
                      [ft.dropdown.Option(str(c[0]), text=f"{c[0]} – {c[1]}") for c in consultores]
        return (
            self._campo("Código empleado", fila[0] if fila else "", solo_lectura=fila is not None),
            self._campo("Nombre completo", fila[1] if fila else ""),
            self._campo("Sueldo", str(fila[2]) if fila else ""),
            self._desplegable("Categoría", [ft.dropdown.Option(n) for n in cats], val_cat),
            self._desplegable("Jefe (opcional)", ops_jefe, str(fila[6]) if fila and fila[6] else ""),
            cats,
        )

    def _guardar_consultor(self, campos, fila=None):
        c_cod, c_nombre, c_sueldo, dd_cat, dd_jefe, cats = campos
        error = ft.Text("", color=C.ERROR, size=T.PEQUEÑO)

        def _al_guardar(_):
            cod    = (c_cod.value or "").strip()
            nombre = (c_nombre.value or "").strip()
            sueldo = (c_sueldo.value or "").strip()
            cat    = dd_cat.value
            jefe   = dd_jefe.value or None

            if (not fila and not cod) or not nombre or not sueldo or not cat:
                error.value = "Todos los campos obligatorios deben completarse."
                error.update(); return
            try:
                sueldo_f = float(sueldo)
            except ValueError:
                error.value = "Sueldo debe ser un número."; error.update(); return

            id_cat   = cats[cat]
            val_jefe = jefe if jefe and jefe != "" else None
            try:
                if fila:
                    self._ejecutar(
                        "UPDATE consultor SET nombre=%s, sueldo=%s, id_categoria=%s, jefe=%s WHERE cod_empleado=%s",
                        (nombre, sueldo_f, id_cat, val_jefe, fila[0]),
                    )
                    self._notificacion("Consultor actualizado.")
                else:
                    self._ejecutar(
                        "INSERT INTO consultor (cod_empleado, nombre, sueldo, id_categoria, jefe) VALUES (%s,%s,%s,%s,%s)",
                        (cod, nombre, sueldo_f, id_cat, val_jefe),
                    )
                    self._notificacion("Consultor creado correctamente.")
                self._cerrar_dialogo(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()

        return _al_guardar, error

    def _abrir_alta(self):
        campos = self._campos_formulario()
        c_cod, c_nombre, c_sueldo, dd_cat, dd_jefe, _ = campos
        al_guardar, error = self._guardar_consultor(campos)
        self._abrir_dialogo("Nuevo consultor",
            ft.Column(controls=[c_cod, c_nombre, c_sueldo, dd_cat, dd_jefe, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _abrir_editar(self, fila):
        campos = self._campos_formulario(fila)
        c_cod, c_nombre, c_sueldo, dd_cat, dd_jefe, _ = campos
        al_guardar, error = self._guardar_consultor(campos, fila)
        self._abrir_dialogo(f"Editar consultor — {fila[0]}",
            ft.Column(controls=[c_cod, c_nombre, c_sueldo, dd_cat, dd_jefe, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _confirmar_baja(self, fila):
        def _eliminar(_):
            try:
                self._ejecutar("DELETE FROM consultor WHERE cod_empleado=%s", (fila[0],))
                self._cerrar_dialogo(); self._recargar()
                self._notificacion("Consultor eliminado.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialogo(); self._notificacion(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialogo_confirmacion(
            "Confirmar eliminación",
            f"¿Eliminás al consultor {fila[1]} ({fila[0]})?",
            "Esta acción no se puede deshacer.", _eliminar,
        )

    def build(self):
        return self._construir_vista(dict(
            etiqueta_dd="Categoría", opciones_dd=self._categorias(),
            al_seleccionar_dd=self._al_seleccionar_dd,
            etiqueta_busqueda="Buscar por nombre o cód.",
            etiqueta_nuevo="Nuevo consultor",
        ))


class VistaCategorias(VistaBase):

    _SQL = "SELECT id_categoria, nombre, salario_rec FROM categoria {where} ORDER BY id_categoria"

    def _columnas(self):
        return [self._col("ID"), self._col("NOMBRE"), self._col("SALARIO REC."), self._col("")]

    def _hacer_filas(self, filas):
        return [ft.DataRow(cells=[
            self._celda(f[0], mono=True), self._celda(f[1]),
            self._celda(f"${f[2]:,.2f}"), self._acciones_celda(f),
        ]) for f in filas]

    def _sql_todas(self): return self._SQL.format(where="")
    def _al_seleccionar_dd(self, _): pass

    def _al_buscar_uno(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._consultar(self._SQL.format(where="WHERE nombre LIKE %s"), (f"%{texto}%",)))

    def _campos_formulario(self, fila=None):
        return (self._campo("Nombre", fila[1] if fila else ""),
                self._campo("Salario recomendado", str(fila[2]) if fila else ""))

    def _guardar_categoria(self, c_nombre, c_salario, fila=None):
        error = ft.Text("", color=C.ERROR, size=T.PEQUEÑO)
        def _al_guardar(_):
            nombre  = (c_nombre.value or "").strip()
            salario = (c_salario.value or "").strip()
            if not nombre or not salario:
                error.value = "Completá todos los campos."; error.update(); return
            try:
                if fila:
                    self._ejecutar("UPDATE categoria SET nombre=%s, salario_rec=%s WHERE id_categoria=%s",
                                   (nombre, float(salario), fila[0]))
                    self._notificacion("Categoría actualizada.")
                else:
                    self._ejecutar("INSERT INTO categoria (nombre, salario_rec) VALUES (%s, %s)",
                                   (nombre, float(salario)))
                    self._notificacion("Categoría creada.")
                self._cerrar_dialogo(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _al_guardar, error

    def _abrir_alta(self):
        c_n, c_s = self._campos_formulario()
        al_guardar, error = self._guardar_categoria(c_n, c_s)
        self._abrir_dialogo("Nueva categoría",
            ft.Column(controls=[c_n, c_s, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _abrir_editar(self, fila):
        c_n, c_s = self._campos_formulario(fila)
        al_guardar, error = self._guardar_categoria(c_n, c_s, fila)
        self._abrir_dialogo(f"Editar categoría — {fila[1]}",
            ft.Column(controls=[c_n, c_s, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _confirmar_baja(self, fila):
        def _eliminar(_):
            try:
                self._ejecutar("DELETE FROM categoria WHERE id_categoria=%s", (fila[0],))
                self._cerrar_dialogo(); self._recargar()
                self._notificacion("Categoría eliminada.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialogo(); self._notificacion(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialogo_confirmacion("Confirmar eliminación",
            f"¿Eliminás la categoría «{fila[1]}»?", "Esta acción no se puede deshacer.", _eliminar)

    def build(self):
        return self._construir_vista(dict(
            etiqueta_dd="—", opciones_dd=[], al_seleccionar_dd=self._al_seleccionar_dd,
            etiqueta_busqueda="Buscar por nombre", etiqueta_nuevo="Nueva categoría",
        ))


class VistaEmpresas(VistaBase):

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

    def _hacer_filas(self, filas):
        return [ft.DataRow(cells=[
            self._celda(f[0], mono=True), self._celda(f[1]), self._celda(f[2]),
            self._celda_atenuada(f[3]), self._acciones_celda(f),
        ]) for f in filas]

    def _sql_todas(self): return self._SQL.format(where="")
    def _al_seleccionar_dd(self, _): pass

    def _al_buscar_uno(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._consultar(
                self._SQL.format(where="WHERE ec.nombre LIKE %s OR ec.cif LIKE %s"),
                (f"%{texto}%", f"%{texto}%"),
            ))

    def _campos_formulario(self, fila=None):
        return (
            self._campo("CIF", fila[0] if fila else "", solo_lectura=fila is not None),
            self._campo("Nombre empresa", fila[1] if fila else ""),
            self._campo("Dirección", fila[2] if fila else ""),
            self._campo("Teléfono(s)", fila[3].replace(" / ", ", ") if fila and fila[3] else "", pista="Separados por coma"),
        )

    def _guardar_telefonos(self, cif, telefonos_raw):
        self._ejecutar("DELETE FROM telefono_cliente WHERE cif=%s", (cif,))
        for tel in telefonos_raw.split(","):
            if t := tel.strip():
                self._ejecutar("INSERT INTO telefono_cliente (cif, telefono) VALUES (%s,%s)", (cif, t))

    def _guardar_empresa(self, c_cif, c_nombre, c_dir, c_tel, fila=None):
        error = ft.Text("", color=C.ERROR, size=T.PEQUEÑO)
        def _al_guardar(_):
            cif    = (c_cif.value or "").strip()
            nombre = (c_nombre.value or "").strip()
            dir_   = (c_dir.value or "").strip()
            if not nombre or (not fila and not cif):
                error.value = "CIF y nombre son obligatorios."; error.update(); return
            try:
                if fila:
                    self._ejecutar("UPDATE empresa_cliente SET nombre=%s, direccion=%s WHERE cif=%s",
                                   (nombre, dir_, fila[0]))
                    self._guardar_telefonos(fila[0], c_tel.value or "")
                    self._notificacion("Empresa actualizada.")
                else:
                    self._ejecutar("INSERT INTO empresa_cliente (cif, nombre, direccion) VALUES (%s,%s,%s)",
                                   (cif, nombre, dir_))
                    self._guardar_telefonos(cif, c_tel.value or "")
                    self._notificacion("Empresa creada.")
                self._cerrar_dialogo(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _al_guardar, error

    def _abrir_alta(self):
        c_c, c_n, c_d, c_t = self._campos_formulario()
        al_guardar, error = self._guardar_empresa(c_c, c_n, c_d, c_t)
        self._abrir_dialogo("Nueva empresa cliente",
            ft.Column(controls=[c_c, c_n, c_d, c_t, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _abrir_editar(self, fila):
        c_c, c_n, c_d, c_t = self._campos_formulario(fila)
        al_guardar, error = self._guardar_empresa(c_c, c_n, c_d, c_t, fila)
        self._abrir_dialogo(f"Editar empresa — {fila[0]}",
            ft.Column(controls=[c_c, c_n, c_d, c_t, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _confirmar_baja(self, fila):
        def _eliminar(_):
            try:
                self._ejecutar("DELETE FROM telefono_cliente WHERE cif=%s", (fila[0],))
                self._ejecutar("DELETE FROM empresa_cliente WHERE cif=%s", (fila[0],))
                self._cerrar_dialogo(); self._recargar()
                self._notificacion("Empresa eliminada.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialogo(); self._notificacion(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialogo_confirmacion("Confirmar eliminación",
            f"¿Eliminás la empresa «{fila[1]}» (CIF: {fila[0]})?",
            "Se eliminarán también sus teléfonos.", _eliminar)

    def build(self):
        return self._construir_vista(dict(
            etiqueta_dd="—", opciones_dd=[], al_seleccionar_dd=self._al_seleccionar_dd,
            etiqueta_busqueda="Buscar por nombre o CIF", etiqueta_nuevo="Nueva empresa",
        ))


class VistaProyectos(VistaBase):

    _SQL = "SELECT id_proyecto, descripcion, coste FROM proyecto {where} ORDER BY id_proyecto"

    def _columnas(self):
        return [self._col("ID"), self._col("DESCRIPCIÓN"), self._col("COSTE INTERNO"),
                self._col("EQUIPO"), self._col("")]

    def _contar_equipo(self, id_proyecto):
        filas = self._consultar("SELECT COUNT(*) FROM consultor_proyecto WHERE id_proyecto = %s", (id_proyecto,))
        return filas[0][0] if filas else 0

    def _chip_equipo(self, cantidad):
        return ft.Container(
            content=ft.Row(controls=[
                ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=13, color=C.PRIMARIO),
                ft.Text(str(cantidad), size=T.PEQUEÑO, color=C.PRIMARIO, weight=ft.FontWeight.W_600),
            ], spacing=4, tight=True),
            bgcolor=C.PRIMARIO_FONDO, border_radius=R.CH,
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
        )

    def _hacer_filas(self, filas):
        return [ft.DataRow(cells=[
            self._celda(f[0], mono=True), self._celda(f[1]),
            self._celda(f"${f[2]:,.2f}"),
            ft.DataCell(self._chip_equipo(self._contar_equipo(f[0]))),
            self._acciones_celda_proyecto(f),
        ]) for f in filas]

    def _acciones_celda_proyecto(self, fila):
        def _ibtn(icono, color, tooltip, manejador):
            return ft.IconButton(
                icon=icono, icon_size=16, icon_color=color, tooltip=tooltip,
                style=ft.ButtonStyle(overlay_color=C.PRIMARIO_FONDO if color != C.ERROR else C.ERROR_FONDO,
                                     shape=ft.RoundedRectangleBorder(radius=R.CH)),
                on_click=lambda _, f=fila: manejador(f),
            )
        return ft.DataCell(ft.Row(controls=[
            _ibtn(ft.Icons.GROUP_OUTLINED,    C.EXITO,   "Gestionar equipo",   self._abrir_equipo),
            _ibtn(ft.Icons.BUSINESS_OUTLINED, C.PRIMARIO,"Empresas clientes",  self._abrir_empresas),
            _ibtn(ft.Icons.EDIT_OUTLINED,     C.PRIMARIO,"Editar",             self._abrir_editar),
            _ibtn(ft.Icons.DELETE_OUTLINE,    C.ERROR,   "Eliminar",           self._confirmar_baja),
        ], spacing=2, tight=True))

    def _sql_todas(self): return self._SQL.format(where="")
    def _al_seleccionar_dd(self, _): pass

    def _al_buscar_uno(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._consultar(
                self._SQL.format(where="WHERE descripcion LIKE %s OR id_proyecto LIKE %s"),
                (f"%{texto}%", f"%{texto}%"),
            ))

    def _campos_formulario(self, fila=None):
        return (self._campo("Descripción", fila[1] if fila else ""),
                self._campo("Coste interno", str(fila[2]) if fila else ""))

    def _guardar_proyecto(self, c_desc, c_coste, fila=None):
        error = ft.Text("", color=C.ERROR, size=T.PEQUEÑO)
        def _al_guardar(_):
            desc  = (c_desc.value or "").strip()
            coste = (c_coste.value or "").strip()
            if not desc or not coste:
                error.value = "Completá todos los campos."; error.update(); return
            try:
                if fila:
                    self._ejecutar("UPDATE proyecto SET descripcion=%s, coste=%s WHERE id_proyecto=%s",
                                   (desc, float(coste), fila[0]))
                    self._notificacion("Proyecto actualizado.")
                else:
                    self._ejecutar("INSERT INTO proyecto (descripcion, coste) VALUES (%s,%s)",
                                   (desc, float(coste)))
                    self._notificacion("Proyecto creado.")
                self._cerrar_dialogo(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _al_guardar, error

    def _abrir_alta(self):
        c_d, c_c = self._campos_formulario()
        al_guardar, error = self._guardar_proyecto(c_d, c_c)
        self._abrir_dialogo("Nuevo proyecto",
            ft.Column(controls=[c_d, c_c, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _abrir_editar(self, fila):
        c_d, c_c = self._campos_formulario(fila)
        al_guardar, error = self._guardar_proyecto(c_d, c_c, fila)
        self._abrir_dialogo(f"Editar proyecto — {fila[0]}",
            ft.Column(controls=[c_d, c_c, error], spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _confirmar_baja(self, fila):
        def _eliminar(_):
            try:
                self._ejecutar("DELETE FROM consultor_proyecto WHERE id_proyecto=%s", (fila[0],))
                self._ejecutar("DELETE FROM proyecto WHERE id_proyecto=%s", (fila[0],))
                self._cerrar_dialogo(); self._recargar()
                self._notificacion("Proyecto eliminado.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialogo(); self._notificacion(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialogo_confirmacion("Confirmar eliminación",
            f"¿Eliminás el proyecto #{fila[0]}?", "Esta acción no se puede deshacer.", _eliminar)

    def _panel_relacion(self, id_entidad, titulo_dialogo, etiqueta_lista, etiqueta_vacia,
                        etiqueta_dd, sql_todos, sql_asignados, icono_fila,
                        sql_insertar, sql_quitar, col_pk, error_seleccion):
        lista   = ft.Column(spacing=E.XCH, tight=True)
        error   = ft.Text("", color=C.ERROR, size=T.PEQUEÑO)
        todos   = self._consultar(sql_todos)
        dd      = self._desplegable(etiqueta_dd,
                                    [ft.dropdown.Option(str(f[0]), text=str(f[1])) for f in todos])

        def _pagina(): return self._tabla.page if self._tabla else None

        def _refrescar():
            asignados = self._consultar(sql_asignados, (id_entidad,))
            lista.controls.clear()
            if not asignados:
                lista.controls.append(ft.Text(etiqueta_vacia, size=T.PEQUEÑO, color=C.TEXTO_SEC))
            else:
                for a in asignados:
                    pk, nombre, subtitulo = a[0], a[1], a[2] if len(a) > 2 else ""

                    def _quitar(_, p=pk):
                        try:
                            self._ejecutar(sql_quitar, (id_entidad, p))
                            error.value = ""
                            _refrescar()
                            self._todas_las_filas = self._consultar(self._sql_todas())
                            self._tabla.rows = self._hacer_filas(self._todas_las_filas)
                            if pg := _pagina(): pg.update()
                        except Exception as ex:
                            error.value = f"Error: {ex}"
                            if pg := _pagina(): pg.update()

                    lista.controls.append(ft.Container(
                        content=ft.Row(controls=[
                            ft.Container(content=ft.Icon(icono_fila, size=14, color=C.PRIMARIO),
                                         bgcolor=C.PRIMARIO_FONDO, border_radius=R.CH,
                                         padding=ft.padding.all(4)),
                            ft.Column(controls=[
                                ft.Text(nombre, size=T.CUERPO, color=C.TEXTO, weight=ft.FontWeight.W_500),
                                ft.Text(subtitulo, size=T.PEQUEÑO, color=C.TEXTO_SEC),
                            ], spacing=0, tight=True, expand=True),
                            ft.IconButton(
                                icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                                icon_size=16, icon_color=C.ERROR, tooltip="Quitar",
                                style=ft.ButtonStyle(overlay_color=C.ERROR_FONDO,
                                                     shape=ft.RoundedRectangleBorder(radius=R.CH)),
                                on_click=_quitar,
                            ),
                        ], spacing=E.CH, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=C.FONDO, border=ft.border.all(1, C.BORDE),
                        border_radius=R.MD,
                        padding=ft.padding.symmetric(horizontal=E.CH, vertical=E.XCH),
                    ))
            if pg := _pagina(): pg.update()

        def _agregar(_):
            val = dd.value
            if not val:
                error.value = error_seleccion
                if pg := _pagina(): pg.update()
                return
            try:
                self._ejecutar(sql_insertar, (id_entidad, int(val) if val.isdigit() else val))
                dd.value = None; error.value = ""
                _refrescar()
                self._todas_las_filas = self._consultar(self._sql_todas())
                self._tabla.rows = self._hacer_filas(self._todas_las_filas)
                if pg := _pagina(): pg.update()
            except Exception as ex:
                error.value = f"Error: {ex}"
                if pg := _pagina(): pg.update()

        _refrescar()
        contenido = ft.Column(controls=[
            ft.Text(etiqueta_lista, size=T.PEQUEÑO, color=C.TEXTO_SEC, weight=ft.FontWeight.W_600),
            ft.Container(content=lista, bgcolor=C.SUPERFICIE, border_radius=R.MD,
                         padding=E.CH, border=ft.border.all(1, C.BORDE)),
            dd,
            ft.Row(controls=[
                ft.Container(expand=True),
                self._btn_accion("Agregar", ft.Icons.ADD, C.PRIMARIO, _agregar),
            ]),
            error,
        ], spacing=E.CH, tight=True)

        self._abrir_dialogo(titulo_dialogo, contenido,
                            [self._btn_accion("Cerrar", ft.Icons.CLOSE, C.TEXTO_SEC,
                                              lambda _: self._cerrar_dialogo())])

    def _abrir_equipo(self, fila):
        self._panel_relacion(
            id_entidad=fila[0],
            titulo_dialogo=f"Equipo — Proyecto #{fila[0]}",
            etiqueta_lista="Consultores asignados",
            etiqueta_vacia="Sin consultores asignados.",
            etiqueta_dd="Agregar consultor",
            sql_todos="SELECT cod_empleado, nombre FROM consultor ORDER BY nombre",
            sql_asignados="""
                SELECT c.cod_empleado, c.nombre, cat.nombre
                FROM consultor_proyecto cp
                JOIN consultor c   ON c.cod_empleado = cp.cod_empleado
                JOIN categoria cat ON cat.id_categoria = c.id_categoria
                WHERE cp.id_proyecto = %s ORDER BY c.nombre
            """,
            icono_fila=ft.Icons.PERSON_OUTLINE,
            sql_insertar="INSERT IGNORE INTO consultor_proyecto (id_proyecto, cod_empleado) VALUES (%s,%s)",
            sql_quitar="DELETE FROM consultor_proyecto WHERE id_proyecto=%s AND cod_empleado=%s",
            col_pk="cod_empleado",
            error_seleccion="Seleccioná un consultor.",
        )

    def _abrir_empresas(self, fila):
        self._panel_relacion(
            id_entidad=fila[0],
            titulo_dialogo=f"Empresas clientes — Proyecto #{fila[0]}",
            etiqueta_lista="Empresas asignadas",
            etiqueta_vacia="Sin empresas asignadas.",
            etiqueta_dd="Agregar empresa cliente",
            sql_todos="SELECT cif, nombre FROM empresa_cliente ORDER BY nombre",
            sql_asignados="""
                SELECT ec.cif, ec.nombre, ec.direccion
                FROM proyecto_empresa pe
                JOIN empresa_cliente ec ON ec.cif = pe.cif
                WHERE pe.id_proyecto = %s ORDER BY ec.nombre
            """,
            icono_fila=ft.Icons.BUSINESS_OUTLINED,
            sql_insertar="INSERT IGNORE INTO proyecto_empresa (id_proyecto, cif) VALUES (%s,%s)",
            sql_quitar="DELETE FROM proyecto_empresa WHERE id_proyecto=%s AND cif=%s",
            col_pk="cif",
            error_seleccion="Seleccioná una empresa.",
        )

    def build(self):
        return self._construir_vista(dict(
            etiqueta_dd="—", opciones_dd=[], al_seleccionar_dd=self._al_seleccionar_dd,
            etiqueta_busqueda="Buscar por descripción o ID", etiqueta_nuevo="Nuevo proyecto",
        ))


class VistaVentas(VistaBase):

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

    def _hacer_filas(self, filas):
        return [ft.DataRow(cells=[
            self._celda(f[0], mono=True), self._celda(f[1]),
            self._celda(f[2], mono=True), self._celda(f[3]),
            self._celda(f"${f[4]:,.2f}"),
            self._celda_atenuada(f[5]), self._celda_atenuada(f[6]),
            self._acciones_celda(f),
        ]) for f in filas]

    def _sql_todas(self): return self._SQL.format(where="")

    def _empresas(self):
        return [f[0] for f in self._consultar("SELECT nombre FROM empresa_cliente ORDER BY nombre")]

    def _empresas_dict(self):
        return {f[1]: f[0] for f in self._consultar("SELECT cif, nombre FROM empresa_cliente ORDER BY nombre")}

    def _al_seleccionar_dd(self, empresa):
        self._actualizar_tabla(self._consultar(self._SQL.format(where="WHERE ec.nombre = %s"), (empresa,)))

    def _al_buscar_uno(self, texto):
        texto = (texto or "").strip()
        if texto:
            self._actualizar_tabla(self._consultar(
                self._SQL.format(where="WHERE v.id_venta LIKE %s OR c.nombre LIKE %s OR ec.nombre LIKE %s"),
                (f"%{texto}%", f"%{texto}%", f"%{texto}%"),
            ))

    def _campos_formulario(self, fila=None):
        empresas  = self._empresas_dict()
        proyectos = self._consultar("SELECT id_proyecto, descripcion FROM proyecto ORDER BY id_proyecto")
        consults  = self._consultar("SELECT cod_empleado, nombre FROM consultor ORDER BY nombre")
        val_emp   = next((n for n, c in empresas.items() if c == (fila[7] if fila else None)), None)
        return (
            self._desplegable("Empresa cliente", [ft.dropdown.Option(n) for n in empresas], val_emp),
            self._desplegable("Proyecto",
                [ft.dropdown.Option(str(p[0]), text=f"{p[0]} – {p[1][:40]}") for p in proyectos],
                str(fila[2]) if fila else None),
            self._desplegable("Consultor",
                [ft.dropdown.Option(str(c[0]), text=f"{c[0]} – {c[1]}") for c in consults],
                str(fila[8]) if fila else None),
            self._campo("Precio de venta", str(fila[4]) if fila else ""),
            self._campo("Fecha inicio (AAAA-MM-DD)", str(fila[5]) if fila else "", pista="2024-01-15"),
            self._campo("Fecha fin (AAAA-MM-DD)",    str(fila[6]) if fila else "", pista="2024-12-31"),
            empresas,
        )

    def _guardar_venta(self, campos, fila=None):
        dd_emp, dd_proy, dd_cons, c_precio, c_inicio, c_fin, empresas = campos
        error = ft.Text("", color=C.ERROR, size=T.PEQUEÑO)

        def _sincronizar(cif, proy):
            self._ejecutar("INSERT IGNORE INTO consultor_proyecto (cod_empleado, id_proyecto) VALUES (%s,%s)",
                           (dd_cons.value, int(proy)))
            self._ejecutar("INSERT IGNORE INTO proyecto_empresa (id_proyecto, cif) VALUES (%s,%s)",
                           (int(proy), cif))

        def _al_guardar(_):
            emp    = dd_emp.value
            proy   = dd_proy.value
            cons   = dd_cons.value
            precio = (c_precio.value or "").strip()
            inicio = (c_inicio.value or "").strip()
            fin    = (c_fin.value or "").strip()
            if not all([emp, proy, cons, precio, inicio, fin]):
                error.value = "Todos los campos son obligatorios."; error.update(); return
            try:
                cif = empresas[emp]
                if fila:
                    self._ejecutar(
                        "UPDATE venta SET cif=%s, id_proyecto=%s, cod_empleado=%s, precio=%s, fecha_inicio=%s, fecha_fin=%s WHERE id_venta=%s",
                        (cif, int(proy), cons, float(precio), inicio, fin, fila[0]),
                    )
                    self._notificacion("Venta actualizada.")
                else:
                    self._ejecutar(
                        "INSERT INTO venta (cif, id_proyecto, cod_empleado, precio, fecha_inicio, fecha_fin) VALUES (%s,%s,%s,%s,%s,%s)",
                        (cif, int(proy), cons, float(precio), inicio, fin),
                    )
                    self._notificacion("Venta registrada.")
                _sincronizar(cif, proy)
                self._cerrar_dialogo(); self._recargar()
            except Exception as ex:
                error.value = f"Error: {ex}"; error.update()
        return _al_guardar, error

    def _abrir_alta(self):
        campos = self._campos_formulario()
        dd_emp, dd_proy, dd_cons, c_precio, c_inicio, c_fin, _ = campos
        al_guardar, error = self._guardar_venta(campos)
        self._abrir_dialogo("Nueva venta",
            ft.Column(controls=[dd_emp, dd_proy, dd_cons, c_precio, c_inicio, c_fin, error],
                      spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _abrir_editar(self, fila):
        campos = self._campos_formulario(fila)
        dd_emp, dd_proy, dd_cons, c_precio, c_inicio, c_fin, _ = campos
        al_guardar, error = self._guardar_venta(campos, fila)
        self._abrir_dialogo(f"Editar venta — #{fila[0]}",
            ft.Column(controls=[dd_emp, dd_proy, dd_cons, c_precio, c_inicio, c_fin, error],
                      spacing=E.MD, tight=True),
            self._acciones_dialogo(al_guardar))

    def _confirmar_baja(self, fila):
        def _eliminar(_):
            try:
                self._ejecutar("DELETE FROM venta WHERE id_venta=%s", (fila[0],))
                self._cerrar_dialogo(); self._recargar()
                self._notificacion("Venta eliminada.", color=C.ERROR)
            except Exception as ex:
                self._cerrar_dialogo(); self._notificacion(f"Error al eliminar: {ex}", color=C.ERROR)
        self._dialogo_confirmacion("Confirmar eliminación",
            f"¿Eliminás la venta #{fila[0]} ({fila[1]})?",
            "Esta acción no se puede deshacer.", _eliminar)

    def build(self):
        return self._construir_vista(dict(
            etiqueta_dd="Empresa", opciones_dd=self._empresas(),
            al_seleccionar_dd=self._al_seleccionar_dd,
            etiqueta_busqueda="Buscar por ID, consultor o empresa",
            etiqueta_nuevo="Nueva venta",
        ))


def vista_consultores(conn, u): return VistaConsultores(conn, u).build()
def vista_categorias(conn, u):  return VistaCategorias(conn, u).build()
def vista_empresas(conn, u):    return VistaEmpresas(conn, u).build()
def vista_proyectos(conn, u):   return VistaProyectos(conn, u).build()
def vista_ventas(conn, u):      return VistaVentas(conn, u).build()
