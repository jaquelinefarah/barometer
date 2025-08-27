# components/theme.py
import plotly.graph_objects as go
import plotly.express as px

# --- Palette / tokens ---
NAVY_BG = "#0E1333"     # fundo navy (combina com sua sidebar)
LIGHT_BG = "#FFFFFF"    # opção caso queira fundo claro
TEXT_DARK = "#17193B"
TEXT_LIGHT = "#FFFFFF"
GRID_LIGHT = "rgba(255,255,255,0.08)"
GRID_DARK = "rgba(23,25,59,0.12)"  # grid sutil para fundo claro

COLORWAY = [
    "#29b5e8",  # azul
    "#FF9F36",  # laranja
    "#D45B90",  # magenta
    "#7D44CF",  # roxo
    "#22c55e",  # verde
    "#FF6B6B",  # vermelho
]

def set_px_defaults(dark: bool = True):
    """
    Define defaults globais do Plotly Express (opcional).
    Chame uma vez no começo do app.
    """
    px.defaults.colorway = COLORWAY
    px.defaults.width = None      # deixa o st.plotly_chart controlar
    px.defaults.height = 320
    px.defaults.template = "plotly_dark" if dark else "plotly_white"

def apply_plotly_theme(
    fig: go.Figure,
    *,
    dark: bool = True,
    font_family: str = "Inter, sans-serif",
    base_font_size: int = 12,
    axis_title_size: int = 14,
    tick_size: int = 12,
    legend_size: int = 12,
):
    """
    Aplica o tema consistente ao Figure (tipografia, eixos, legendas, fundos).
    - dark=True -> fundo navy com texto claro
    - dark=False -> fundo claro com texto escuro
    """
    bg = NAVY_BG if dark else LIGHT_BG
    text = TEXT_LIGHT if dark else TEXT_DARK
    grid = GRID_LIGHT if dark else GRID_DARK

    fig.update_layout(
        font=dict(family=font_family, size=base_font_size, color=text),

        xaxis=dict(
            title_font=dict(size=axis_title_size),
            tickfont=dict(size=tick_size),
            gridcolor=grid,
            zerolinecolor=grid,
            linecolor=grid,
            ticks="outside",
        ),
        yaxis=dict(
            title_font=dict(size=axis_title_size),
            tickfont=dict(size=tick_size),
            gridcolor=grid,
            zerolinecolor=grid,
            linecolor=grid,
            ticks="outside",
        ),

        legend=dict(font=dict(size=legend_size)),
        plot_bgcolor=bg,
        paper_bgcolor=bg,
        margin=dict(l=40, r=20, t=40, b=40),
    )
    return fig

def new_figure(*, dark: bool = True) -> go.Figure:
    """
    Cria um Figure vazio já com o tema aplicado.
    """
    fig = go.Figure()
    return apply_plotly_theme(fig, dark=dark)
