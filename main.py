import pandas as pd
import plotly.express as px
from datetime import datetime
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import dash_auth
from funciones_modificado import obtener_metrica_gasolina, porcentaje_reglaDeTres
from funciones_modificado import construir_barras_mensual as construir_barras_cpa
from Datos_inventados import get_audience_graph, get_gender_graph, get_ciudades_table

# ── 1) Carga de datos y fecha de análisis ────────────────────────────────────
df_main   = pd.read_excel("./Dat_App.xlsx")
df_main["Fecha"] = pd.to_datetime(df_main["Fecha"])
fecha_main = pd.to_datetime("2025-05-30").date()
hoy = datetime.now()
#####################################################################################
# 1) Carga del DataFrame
df_alcance_dia = pd.read_excel("./Graf_alc_App.xlsx")
df_alcance_dia["Fecha"] = pd.to_datetime(df_alcance_dia["Fecha"])

# ── 1.1) Extraer el Score dinámico para campaña Ecommer en esa fecha ─────────
mask_score = ((df_main["Fecha"].dt.date  == fecha_main) & (df_main["Tipo de Campaña"]     == "Ecommer"))
if mask_score.any():
    valor_score = float(df_main.loc[mask_score, "Score"].iloc[0])
else:
    valor_score = 0.0  # o el valor por defecto que prefieras

# ── 2) Métricas principales (verde/orange) ────────────────────────────────────
METRICAS = [
    ("Inversión",     "Inversión",     "Obj_mensual Inversión",     True),
    ("Ventas",         "Ventas",        "Obj_mensual Ventas",       False),
    ("Impresiones",   "Impresiones",   "Obj_mensual Impresiones",   False),
    ("Alcance",       "Alcance",       "Obj_mensual Alcance",       False),
    ("Clicks",        "Clicks",        "Obj_mensual Clicks",        False),
    ("Views",         "Views",         "Obj_mensual Views",         False),
    ("Conversiones",  "Conversiones",  "Obj_mensual Conversiones",  False),
]
#───────────────────────────────canales ─────────────────────────────── Hecsari
df_ventas = pd.read_excel("./ads_df_day_Vc.xlsx")
df_ventas["Fecha"] = pd.to_datetime(df_ventas["Fecha"])
fecha_ventas = pd.to_datetime("2025-05-31").date()
df_ventas = df_ventas.groupby('Plataforma')['Ventas Acumulada'].last().reset_index()
df_ventas = df_ventas.rename(columns={"Ventas Acumulada": "Valor"})
#######
df_alcance = pd.read_excel("./ads_df_day_Ac_1.xlsx")
df_alcance["Fecha"] = pd.to_datetime(df_alcance["Fecha"])
fecha_alcance = pd.to_datetime("2025-05-31").date()
df_alcance = df_alcance.groupby('Plataforma')['Alcance Acumulada'].last().reset_index()
df_alcance = df_alcance.rename(columns={"Alcance Acumulada": "Valor"})


# ── 3) Genera bloques principales ────────────────────────────────────────────
bloques_main = []
for nombre, col_val, col_obj, inv in METRICAS:
    if col_val not in df_main or col_obj not in df_main:
        continue
    actual, objetivo, pos = obtener_metrica_gasolina(df_main, fecha_main, col_val = col_val, col_mensual = col_obj, invertida = inv )
    pct = porcentaje_reglaDeTres(actual, objetivo)
    # build_bar viene de tu funciones.py
    bloques_main.append(
        html.Div([html.H4(nombre, className="titulo"),
                  html.Div([
                    html.Div(className="barra-color-invertida" if inv else "barra-color"),
                    html.Div(pct, className="marcador", style={"left": pos}),
                    html.Div("0%", className="minimo",  style={"left":"0%"}),
                    html.Div("100%", className="maximo", style={"left":"100%"})
                  ], className="contenedor-barra")
        ])
    )
# ── 4) Métricas CPA / Ticket Promedio ────────────────────────────────────────
METRICAS_CPA = [
    ("CPA",             "CPA",                        "CPA Promedio Acumulado",   "Obj_mensual CPA",        True),
    ("Ticket Prom.",    "Ticket Promedio",            "Ticket Promedio Acumulado","Obj_mensual Ticket Prom",True),
]
bloques_cpa = construir_barras_cpa( df_main, fecha_main, METRICAS_CPA, campana="Ecommer")

#VALID_USERNAME_PASSWORD_PAIRS = {
#    'webapp-hashtag': 's92i$J4osPKg'
#}#no borrar
#Usuario=[['webapp-hashtag','webapp-hashtag2'],['s92i$J4osPKg','s92i$J4osPKg2']]
# ── 5) Montaje final de la App ───────────────────────────────────────────────
app = Dash(__name__, assets_folder="assets")
#auth=dash_auth.BasicAuth(app, Usuario)
app.layout = html.Div([

    # ——— Encabezado —————————————
    html.Div("BRAIN", className="titulo-brain"),
    html.Div([
       html.Div(f"{valor_score:.2f}", className="burbuja-score"),#html.Div("9.75", className="burbuja-score"),
      html.Div("Bienvenido, Hashtag", className="welcome-text"),
      html.Div(f"Última Actualización: {hoy.strftime('%d %b %Y, %H:%M')}", className="update-text"),
    ], className="contenedor-indicador"),

    # ——— Un único contenedor para TODAS las barrinhas ——————————
    html.Div([
        # 1) Barras principales
        *bloques_main,
        # 2) Separador interno (opcional)
#        html.Hr(className="separador-interno"),
        # 3) Barras CPA/Ticket
        *bloques_cpa
    ], className="barras-container"),

    # ——— Secciones adicionales ——————————
    html.Hr(className="separador"),
    html.H4("Audiencia Alcanzada", className="titulo"),
    #get_audience_graph(),
    get_audience_graph(df_alcance_dia, fecha_main),

    html.Hr(className="separador"),
    html.H4("Género", className="titulo"),
    get_gender_graph(),

    html.Hr(className="separador"),
    html.H4("Cd’s", className="titulo"),
    get_ciudades_table(),
    
    # _____ Sección: Canales_________
    html.Div([
        dcc.Tabs(id="tabs", value="ventas", children=[
            dcc.Tab(label="Ventas / Leads", value="ventas"),
            dcc.Tab(label="Alcance", value="alcance")
        ], className="tabs-custom"),
        
        dcc.Graph(id="grafico-dashboard", config={"displayModeBar": False})
        ], className="contenedor-dashboard")


], className="contenedor-movil")


@app.callback(
    Output("grafico-dashboard", "figure"),
    Input("tabs", "value")
)
def actualizar_dashboard(tab):
    if tab == "ventas":
        df = df_ventas
        titulo = "Costo por Venta / Lead"
        color = "#f7d76f"
        formato = lambda v: f"${v:.2f}"
    else:
        df = df_alcance
        titulo = "Alcance por Plataforma"
        color = "#7fd1b9"
        formato = lambda v: f"{int(v):,}"

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df["Plataforma"],
        x=df["Valor"],
        orientation='h',
        marker=dict(color=color),
        text=[formato(v) for v in df["Valor"]],
        textposition='outside'
    ))

    fig.update_layout(
        title=titulo,
        title_font=dict(color='white', size=16),
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            showline=False,
            ticks=""
        ),
        yaxis=dict(
            showgrid=False,
            color='white'
        ),
        plot_bgcolor='#1a1a1a',
        paper_bgcolor='#1a1a1a',
        font=dict(color='white'),
        margin=dict(l=80, r=20, t=50, b=30),
        height=320
    )

    return fig

if __name__ == "__main__":
    app.run(debug=True, port=8050)

