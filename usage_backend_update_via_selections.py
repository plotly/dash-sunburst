import dash
from dash.dependencies import Input, Output, State
import dash_sunburst
import dash_core_components as dcc
import dash_html_components as html


N_CHILDREN = 3


def create_data(start_level_index, node_index):
    data = {
        'name': 'Level {}, Item {}'.format(start_level_index, node_index),
        'children': [{
            'name': 'Level {}, Item {}'.format(
                start_level_index + 1,
                i + 1
            ),
            'size': 1,
            'children': [{
                'name': 'Level {}, Item {}'.format(
                    start_level_index + 2,
                    j + 1
                ),
                'size': 1
            } for j in range(N_CHILDREN)]
        } for i in range(N_CHILDREN)]
    }
    return data


def extract_level_and_node_from_name(name):
    level = int(name.split(', ')[0].replace('Level ', ''))
    node = int(name.split(', ')[1].replace('Item ', ''))
    return (level, node)


app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([
    dash_sunburst.Sunburst(
        id='sun',
        data=create_data(1, 1),
        selectedPath=[],
    ),
])


@app.callback(Output('sun', 'data'),
              [Input('sun', 'selectedPath')],
              [State('sun', 'data')])
def display_sun(selectedPath, data):
    if len(selectedPath) > 0:
        (level, node) = extract_level_and_node_from_name(selectedPath[-1])
    elif data['name'] == 'Level 1, Item 1':
        # initial state or user is back to the center - don't change anything
        raise dash.exceptions.PreventUpdate()
    else:
        # user clicked on the center node - bring the data back one level
        (level, _) = extract_level_and_node_from_name(data['name'])
        level -= 1
        node = 1
    return create_data(level, node)


if __name__ == '__main__':
    app.run_server(debug=True)
