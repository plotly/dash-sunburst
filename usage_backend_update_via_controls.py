import dash
from dash.dependencies import Input, Output
import dash_sunburst
import dash_core_components as dcc
import dash_html_components as html


N_CHILDREN = 3

def create_data(start_level_index, node_index):
    data = {
        'name': 'Level {}, Node {}'.format(start_level_index, node_index),
        'children': [{
            'name': 'Level {}, Child {}'.format(
                start_level_index + 1,
                i + 1
            ),
            'size': 1,
            'children': [{
                'name': 'Level {}, Child {}'.format(
                    start_level_index + 2,
                    j + 1
                ),
                'size': 1
            } for j in range(N_CHILDREN)]
        } for i in range(N_CHILDREN)]
    }
    return data


app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([
    html.Label('Display Level: '),
    dcc.Dropdown(
        id='level',
        options=[{
            'label': 'Level {}'.format(i),
            'value': i
        } for i in range(1, 10)],
        value=1
    ),
    html.Label('Display node within level'),
    dcc.Dropdown(id='node'),

    dash_sunburst.Sunburst(
        id='sun',
        data=create_data(1, 1),
        updatemode='replace'
    )
])


@app.callback(Output('node', 'options'), [Input('level', 'value')])
def update_node_options(level):
    return [{
        'label': 'Level {}, Node {}'.format(level, i),
        'value': i
    } for i in range(1, N_CHILDREN + 1)]


@app.callback(Output('node', 'value'), [Input('node', 'options')])
def update_node_value(options):
    return options[0]['value']


@app.callback(Output('sun', 'data'), [
    Input('level', 'value'),
    Input('node', 'value')])
def update_sun(level, node):
    return create_data(level, node)


if __name__ == '__main__':
    app.run_server(debug=True)
