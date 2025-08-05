from dash import dash_table, html

# funciones.py

from calendar import monthrange
import pandas as pd
import plotly.express as px
from dash import dcc, html

def get_audience_graph(df_main: pd.DataFrame, fecha_selected: pd.Timestamp) -> html.Div:
    df = df_main.copy()
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    # 1) Filtrar por la fecha seleccionada
    mask = df['Fecha'].dt.date == fecha_selected
    df_fecha = df.loc[mask]
    # 2) Agrupar por Edad y sumar el Alcance acumulado
    audience_df = ( df_fecha
        .groupby('Edad', as_index=False)['Alcance acumulado']
        .sum()
        .rename(columns={'Edad':'segmento', 'Alcance acumulado':'valor_acumulado'})
    )
    # 3) Construir la figura
    fig = px.bar(
        audience_df,
        x='valor_acumulado',
        y='segmento',
        orientation='h',
        labels={'valor_acumulado': 'Alcance Acumulado', 'segmento': ''},
        color_discrete_sequence=['#b19cd9']
    )

    # 4) Ajustes de estilo (igual que antes)
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showgrid=False, showticklabels=False, visible=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showline=False, ticks='', tickfont=dict(color='white'), autorange='reversed')
    fig.update_traces(width=0.4, marker_line_width=0)

    # 5) Devolver el Div con el gráfico
    return html.Div(
        dcc.Graph(
            id='audience-graph',
            figure=fig,
            config={'displayModeBar': False},
            style={'height': '200px'}
        ),
        className='barras-container'
    )

"""
def get_audience_graph():
    import pandas as pd
    import plotly.express as px
    from dash import dcc, html

    # 1) Datos de ejemplo
    audience_df = pd.DataFrame({
        "segmento": ["18 – 25", "25 – 35", "35 – 45", "45 – 55", "+55"],
        "porcentaje": [75, 60, 45, 35, 25]
    })

    # 2) Construye la figura Plotly
    fig = px.bar(
        audience_df,
        x="porcentaje",
        y="segmento",
        orientation="h",
        labels={"porcentaje": "% acumulado", "segmento": ""},
        color_discrete_sequence=["#b19cd9"],
    )

    # 3) Fondo transparente, sin margenes internos y externos
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    # 4) Oculta Eje X por completo
    fig.update_xaxes(showgrid=False, showticklabels=False, visible=False, zeroline=False)

    # 5) Eje Y sin líneas ni ticks, con etiquetas en blanco
    fig.update_yaxes(
        showgrid=False,
        showline=False,
        ticks="",
        tickfont=dict(color="white"),
        autorange="reversed"
    )

    # 6) Ajusta grosor de barras y elimina bordes
    fig.update_traces(width=0.4, marker_line_width=0)

    # 7) Devuelve el Div listo con su clase de contenedor
    return html.Div(
        dcc.Graph(
            id="audience-graph",
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "200px"}
        ),
        className="barras-container"
    )"""
    
#############################################################################################################
def get_gender_graph():
    import pandas as pd
    import plotly.express as px
    from dash import dcc, html

    # 1) Datos de ejemplo para Género
    gender_df = pd.DataFrame({
        "genero": ["H", "M"],
        "porcentaje": [40, 60]
    })

    # 2) Construye la figura Plotly (barras horizontales azul claro)
    fig = px.bar(
        gender_df,
        x="porcentaje",
        y="genero",
        orientation="h",
        labels={"porcentaje": "%", "genero": ""},
        color_discrete_sequence=["#ADD8E6"],   # azul claro
    )

    # 3) Fondo transparente y cero márgenes
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    # 4) Oculta eje X completamente
    fig.update_xaxes(showgrid=False, showticklabels=False, visible=False, zeroline=False)

    # 5) Eje Y sin líneas, con etiquetas en blanco y orden invertido
    fig.update_yaxes(
        showgrid=False,
        showline=False,
        ticks="",
        tickfont=dict(color="white"),
        autorange="reversed"
    )

    # 6) Ajusta grosor de barras
    fig.update_traces(width=0.4, marker_line_width=0)

    # 7) Devuelve el Div con la gráfica
    return html.Div(
        dcc.Graph(
            id="gender-graph",
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "120px"}  # ajusta la altura si quieres
        ),
        className="barras-container"
    )
###########################################################################################################################
import pandas as pd
from dash import dash_table, html

def get_ciudades_table():
    """
    Devuelve un DataTable estilizado para la sección Cd’s.
    """
    # 1) Datos de ejemplo
    df = pd.DataFrame({
        "ventas_leads": [
            "CDMX   $10,000",
            "Monterrey   $15,000",
            "Guadalajara   $18,000",
            "Puebla   $10,000",
            "Querétaro   $15,000"
        ],
        "alcance": [
            "CDMX   1.3 M",
            "Monterrey   1 M",
            "Guadalajara   .9 M",
            "Puebla   .85 M",
            "Querétaro   .5 M"
        ]
    })

    # 2) DataTable sin bordes y texto blanco
    table = dash_table.DataTable(
        columns=[
            {"name": "Ventas / Leads", "id": "ventas_leads"},
            {"name": "Alcance",        "id": "alcance"}
        ],
        data=df.to_dict("records"),
        style_as_list_view=True,  # quita gridlines interiores
        style_table={
            "width": "100%",
            "border": "none",
            "background": "transparent"
        },
        style_header={
            "backgroundColor": "transparent",
            "color": "white",
            "fontWeight": "bold",
            "border": "none",
            "textAlign": "left"
        },
        style_cell={
            "backgroundColor": "transparent",
            "color": "white",
            "border": "none",
            "padding": "4px",
            "textAlign": "left"
        },
        style_cell_conditional=[
            {"if": {"column_id": "ventas_leads"}, "width": "50%"},
            {"if": {"column_id": "alcance"},       "width": "50%"}
        ],
        page_action="none",    # sin paginación
        sort_action="none",    # sin sorting
    )

    # 3) Envuelve en tu contenedor gris
    return html.Div(table, className="barras-container")
