"""Tema Altair del progetto "Non solo Giochi".

Importare il modulo registra e attiva automaticamente il tema:

    import nsg_altair_theme  # noqa: F401

Caratteristiche:
- sfondo trasparente (i grafici non hanno un background proprio: si adattano
  alla pagina in cui sono inseriti);
- palette di progetto a sette colori, usata per le scale categoriche;
- testo e assi scuri, griglia chiara e discreta.
"""

import altair as alt

# Palette di progetto (ordine usato per le scale categoriche).
PALETTE = [
    "#1b2140",  # blu
    "#ff8009",  # arancione
    "#9a0641",  # fucsia
    "#ffe34a",  # giallo
    "#e7b6af",  # rosa
    "#0088b0",  # teal
    "#e03830",  # rosso
]

INK = "#1b2140"      # testo, titoli, assi
GRID = "#e2ddd4"     # griglia e bordi, tenui
MARK = PALETTE[0]    # colore di default dei mark
FONT = "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
FONT_WEIGHT = 400


@alt.theme.register("nsg_altair_theme", enable=True)
def nsg_altair_theme() -> alt.theme.ThemeConfig:
    return {
        "config": {
            # Sfondo trasparente: nessun background proprio del grafico.
            "background": "transparent",
            "view": {
                "continuousWidth": 400,
                "continuousHeight": 300,
                "stroke": None,   # niente cornice attorno all'area del grafico
                "fill": None,     # area del grafico trasparente
            },
            "mark": {"color": MARK},
            "arc": {"fill": MARK},
            "area": {"fill": MARK, "line": True, "fillOpacity": 0.15},
            "line": {"stroke": MARK, "strokeWidth": 2},
            "path": {"stroke": MARK},
            "rect": {"fill": MARK},
            "bar": {"fill": MARK},
            "point": {"fill": MARK, "filled": True},
            "shape": {"stroke": MARK},
            "symbol": {"fill": MARK},

            "title": {
                "color": INK,
                "anchor": "start",
                "fontSize": 15,
                "font": FONT,
                "fontWeight": 600,
                "subtitleColor": INK,
                "subtitleFont": FONT,
            },

            "axis": {
                "labelColor": INK,
                "labelFontSize": 12,
                "labelFont": FONT,
                "labelFontWeight": FONT_WEIGHT,
                "titleColor": INK,
                "titleFont": FONT,
                "titleFontWeight": 600,
                "titleFontSize": 12,
                "grid": True,
                "gridColor": GRID,
                "gridWidth": 0.6,
                "domainColor": GRID,
                "tickColor": GRID,
                "labelAngle": 0,
                "labelPadding": 4,
                "tickSize": 5,
            },

            "axisBand": {"grid": False},

            "legend": {
                "labelFontSize": 11,
                "titleFontSize": 12,
                "labelFont": FONT,
                "titleFont": FONT,
                "labelColor": INK,
                "titleColor": INK,
                "symbolType": "circle",
                "padding": 4,
            },

            "range": {
                "category": PALETTE,
            },
        }
    }
