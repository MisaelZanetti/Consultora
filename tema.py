import flet as ft


class C:
    FONDO         = "#0F1117"
    SUPERFICIE    = "#1A1D27"
    BORDE         = "#2A2D3A"
    DIVISOR       = "#22253A"

    PRIMARIO      = "#3B82F6"
    PRIMARIO_OSC  = "#2563EB"
    PRIMARIO_FONDO= "#1E3A5F"

    TEXTO         = "#F1F5F9"
    TEXTO_SEC     = "#64748B"
    TEXTO_PISTA   = "#475569"

    EXITO         = "#22C55E"
    ERROR         = "#F87171"
    ERROR_FONDO   = "#2D1515"

    BLANCO        = "#F1F5F9"
    BARRA_ACENTO  = "#3B82F6"


class T:
    DISPLAY = 24
    TITULO  = 18
    CUERPO  = 14
    PEQUEÑO = 12
    MICRO   = 11


class E:
    XCH  = 4
    CH   = 8
    MD   = 16
    GD   = 24
    XGD  = 32
    XXG  = 48


class R:
    CH = 4
    MD = 6
    GD = 10


def etiqueta(texto: str, tamaño: int = T.CUERPO, color: str = C.TEXTO_SEC,
             peso=ft.FontWeight.NORMAL) -> ft.Text:
    return ft.Text(texto, size=tamaño, color=color, weight=peso)


def divisor() -> ft.Divider:
    return ft.Divider(height=1, color=C.BORDE)


def insignia(texto: str, color_fondo: str = C.PRIMARIO) -> ft.Container:
    return ft.Container(
        content=ft.Text(texto, size=T.MICRO, color="#FFFFFF", weight=ft.FontWeight.W_600),
        bgcolor=color_fondo,
        border_radius=R.CH,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )
