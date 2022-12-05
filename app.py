import markupsafe
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
from plotly.io import show

app = Dash(__name__)

params = []

ROUTES = 1
COLS = 3
for i in range(ROUTES):
    params.append(f"species-{i}")
    params.append(f"deltas-{i}")


def get_type(param):
    if "spec" in param:
        return "text"
    return "numeric"


app.layout = html.Div(
    [
        dash_table.DataTable(
            id="table-editing-simple",
            columns=([{"id": p, "name": p, "type": get_type(p)} for p in params]),
            data=[dict(**{param: None for param in params}) for i in range(COLS)],
            editable=True,
        ),
        dcc.Graph(id="table-editing-simple-output"),
    ]
)


@app.callback(
    Output("table-editing-simple-output", "figure"),
    Input("table-editing-simple", "data"),
    Input("table-editing-simple", "columns"),
)
def display_output(rows, columns):
    df = pd.DataFrame(rows, columns=[c["name"] for c in columns])

    fig = go.Figure()

    start_at = 5
    line_length = 3
    offset = 5
    starts = []
    end = []
    for i in range(ROUTES):
        deltas = df[f"deltas-{i}"]
        for delta in deltas:
            if delta:

                fig.add_annotation(
                    text="label", x=start_at + 0.1, y=delta + 0.1, showarrow=False
                )
                x = np.array([start_at, start_at + line_length])
                start_at = start_at + line_length + offset
                y = np.array([delta, delta])
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        marker=dict(color="red"),
                        text="label",
                    )
                )
    fig.update_traces(textposition="top center")

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
