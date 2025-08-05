from dash import html
import pandas as pd
from datetime import date

# (App-antes.py) CPA | Ticket_prom
def escalar(v: float) -> float:
    if v < 100:       return 100
    elif v < 1_000:   return 1_000
    elif v < 10_000:  return 10_000
    elif v < 100_000: return 100_000
    else:             return 1_000_000



"""def pos_recta(val, obj, maximo):
    Calcula la posición del valor total:
      - tramo 0–obj ⇒ 0–50%
      - tramo obj–max  ⇒ 50–100%
      - el objetivo siempre queda en 50%

    if obj <= 0 or obj >= maximo:
        return f"{min(val / maximo, 1) * 100:.1f}%"
    if val <= obj:
        return f"{(val / obj) * 50:.1f}%"
    return f"{50 + (val - obj) / (maximo - obj) * 50:.1f}%"
"""
def pos_recta(val, obj, maximo):
    """
    Calcula la posición del valor total en la barra:
      - tramo 0–obj     → 0–50%
      - tramo obj–max   → 50–100%
    Luego recorta (clamp) el resultado a 100% para que la flecha no sobrepase el extremo.
    """
    # 1) calcula el porcentaje interno
    if obj <= 0 or obj >= maximo:
        pct = min(val / maximo, 1) * 100
    elif val <= obj:
        pct = (val / obj) * 50
    else:
        pct = 50 + (val - obj) / (maximo - obj) * 50

    # 2) clamp a 100%
    pct_clamped = min(pct, 100.0)
    return f"{pct_clamped:.1f}%"
################################################################# Barras  con Obj_mensual en medio como el CPA



def bloque(nombre, actual, objetivo, maximo, pos):
    # porcentaje total sobre meta
    porcentaje_actual = f"{(actual / objetivo) * 100:.1f}%" if objetivo > 0 else "0%"

    return html.Div([
        html.H4(nombre, className="titulo"),
        html.Div([
            html.Div(className="barra-color"),
            html.Div(porcentaje_actual, className="marcador", style={"left": pos}),
            html.Div("100%", className="meta-centro", style={"left": "50%"}),
            html.Div("0%", className="minimo", style={"left": "0%"}),
            html.Div("200%", className="maximo", style={"left": "100%"})
        ], className="contenedor-barra")
    ])


def construir_barras(df, fecha_obj, todas_las_metricas, incluir_solo=[]):
    # Asegurarse de que la columna Fecha es datetime
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    # Filtrar todas las filas de la fecha
    df_fecha = df[df["Fecha"] == fecha_obj]
    bloques = []

    for nombre, col_real, col_obj in todas_las_metricas:
        # Filtrado por nombre si se pidió
        if incluir_solo and nombre not in incluir_solo:
            continue
        # Comprobar existencia de columnas
        if col_real not in df_fecha.columns or col_obj not in df_fecha.columns:
            continue

        # Sumar todos los valores de esa fecha
        val = df_fecha[col_real].sum()
        obj = df_fecha[col_obj].sum()

        # Calcular máximo escalado y posición
        mx = escalar(max(val, obj))
        pos = pos_recta(val, obj, mx)

        bloques.append(bloque(nombre, val, obj, mx, pos))

    return bloques


# Función de cálculo de métricas invertidas o no (antes en Fun_chat.py)
"""def obtener_metrica_gasolina( df: pd.DataFrame, fecha: date, col_val: str,  col_mensual: str, invertida: bool):
    df["Fecha"] = pd.to_datetime(df["Fecha"]) ## Objetivo mensual del día (tomo la primera fila encontrada)
    fila = df[df["Fecha"].dt.date == fecha]
    #   OBJETIVO MENSUAL = Σ(Branding + Ecommer) en el día 1
    mask_obj = ((df["Fecha"].dt.year  == fecha.year) & (df["Fecha"].dt.month == fecha.month) &
        (df["Fecha"].dt.day   == 1) & (df["Tipo de Campaña"].isin(["Branding", "Ecommer"])) )
    mensual = df.loc[mask_obj, col_mensual].sum()
    if mensual == 0:                        # salvaguarda para no dividir por cero
        mensual = 1.0    
    #mensual  = float(fila[col_mensual].iloc[0]) if not fila.empty and col_mensual in fila else 1.0
    #  Acumulado del mes hasta la fecha
    mask = ((df["Fecha"].dt.year  == fecha.year) & (df["Fecha"].dt.month == fecha.month) &  (df["Fecha"].dt.date  <= fecha) )
    suma_mes = df.loc[mask, col_val].sum()
    if invertida:
        actual = max(mensual - suma_mes, 0.0)
    else:
        actual = suma_mes
    pct_act = min(max(actual / mensual, 0.0), 1.0) * 100
    # invertida: mapea 100%→0%; normal: 0→100%
    pos_act = f"{(100 - pct_act):.1f}%" if invertida else f"{pct_act:.1f}%"
    #pos_obj = "50%"
    return actual, pos_act #, pos_obj"""

def obtener_metrica_gasolina( df: pd.DataFrame,  fecha: date, col_val: str, col_mensual: str, invertida: bool):
    """
    Devuelve: actual (float), objetivo_mensual (float), pos_act (str)
    """
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    # Objetivo mensual suma de todas las campañas en el 1er día
    mask_obj = (
        (df["Fecha"].dt.year  == fecha.year) &
        (df["Fecha"].dt.month == fecha.month) &
        (df["Fecha"].dt.day   == 1)
    )
    objetivo = df.loc[mask_obj, col_mensual].sum() or 1.0

    mask = (
        (df["Fecha"].dt.year  == fecha.year) &
        (df["Fecha"].dt.month == fecha.month) &
        (df["Fecha"].dt.date  <= fecha)
    )
    acumulado = df.loc[mask, col_val].sum()

    actual = max(objetivo - acumulado, 0.0) if invertida else acumulado
    pct_act = min(max(actual / objetivo, 0.0), 1.0) * 100
    pos_act = f"{(100 - pct_act):.1f}%" if invertida else f"{pct_act:.1f}%"

    return actual, objetivo, pos_act


# ───────────────────────── NUEVA función pedida ───────────────────────────────
def porcentaje_reglaDeTres(actual: float, objetivo: float) -> str:
    """ Regla de tres simple: (actual / objetivo) * 100.   |      Devuelve un string con una cifra decimal y el signo %."""
    if objetivo <= 0:
        return "0%"
    return f"{(actual / objetivo) * 100:.1f}%"


# ______________________ Funciones para las barritas CPA y Tiket promedio ____________________

def pos_recta_vers2(val: float, obj: float, maximo: float) -> str:
    if obj <= 0 or obj >= maximo:
        pct = min(val / maximo, 1) * 100
    elif val <= obj:
        pct = (val / obj) * 50
    else:
        pct = 50 + (val - obj) / (maximo - obj) * 50
    pct = min(pct, 100.0)
    return f"{pct:.1f}%"
############################################################################################################################################

def bloque_mensual( nombre: str,  actual: float, prom_acum: float, objetivo: float, maximo: float, pos_act: str,  pos_acum: str, invertida: bool=False ):
    txt_act  = f"${actual:,.2f}"
    txt_acum = f"${prom_acum:,.2f}"

    return html.Div([
        html.H4(nombre, className="titulo"),
        html.Div([
            # fondo de la barra
            html.Div(className="barra-color-invertida" if invertida else "barra-color"),

            # ► Flecha roja (actual)
            html.Div(txt_act, className="marcador", style={"left": pos_act}),

            # ► Flecha morada (sin texto)
            html.Div("", className="marcador-acum", style={"left": pos_acum}),

            # ► Texto morado abajo de la flecha
            html.Div(txt_acum, className="text-acum", style={"left": pos_acum}),

            # ► Meta mensual en el centro
            html.Div(f"${objetivo:,.0f}", className="meta-centro", style={"left": "50%"}),

            # ► Extremos
            html.Div("0",               className="minimo", style={"left": "0%"}),
            html.Div(f"$", className="maximo", style={"left": "100%"})
        ], className="contenedor-barra")
    ])

######################################################################################################

def construir_barras_mensual(df: pd.DataFrame, fecha_obj: pd.Timestamp, metricas, campana: str = "Ecommer"):
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    mask_obj = ( (df["Fecha"].dt.year  == fecha_obj.year) & (df["Fecha"].dt.month == fecha_obj.month) & (df["Fecha"].dt.day   == 1) )
    bloques = []
    for nombre, col_act, col_acum, col_mensual, invertida in metricas:
        if col_mensual not in df.columns: continue
        objetivo  = df.loc[mask_obj, col_mensual].sum() or 1.0
        mask_act  = ( (df["Fecha"].dt.date       == fecha_obj) & (df["Tipo de Campaña"]     == campana))
        actual    = float(df.loc[mask_act, col_act].iloc[0]) if mask_act.any() else 0.0
        prom_acum = float(df.loc[mask_act, col_acum].iloc[0]) if mask_act.any() else 0.0
        mx        = escalar(max(actual, objetivo))
        pos_act   = pos_recta_vers2(actual,    objetivo, mx)
        pos_acum  = pos_recta_vers2(prom_acum, objetivo, mx)
        bloques.append( bloque_mensual( nombre, actual, prom_acum, objetivo, mx, pos_act, pos_acum, invertida)  )
    return bloques
