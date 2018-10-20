import dash
from dash.dependencies import Input, Output
import dash_sunburst
import dash_html_components as html


N_CHILDREN = 3


def node_name(level_index, node_index):
    return 'Level {}, Node {}'.format(level_index, node_index)


def create_data_from_path(path):
    start_level_index = len(path) + 1
    node_index = extract_level_and_node_from_name(path[-1])[1] if len(path) else 1
    data = {
        'name': node_name(start_level_index, node_index),
        'children': [{
            'name': node_name(start_level_index + 1, i + 1),
            'size': 1,
            'children': [{
                'name': node_name(start_level_index + 2, j + 1),
                'size': 1
            } for j in range(N_CHILDREN)]
        } for i in range(N_CHILDREN)]
    }

    # wrap back down to level 1
    for name in reversed(path[:-1]):
        data = {
            'name': name,
            'children': [data]
        }
    if len(path):
        data = {
            'name': node_name(1, 1),
            'children': [data]
        }
    return data


def extract_level_and_node_from_name(name):
    level = int(name.split(', ')[0].replace('Level ', ''))
    node = int(name.split(', ')[1].replace('Node ', ''))
    return (level, node)


app = dash.Dash(__name__)
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

app.layout = html.Div([
    dash_sunburst.Sunburst(
        id='sun',
        data=create_data_from_path([]),
        selectedPath=[]
    ),
])


@app.callback(Output('sun', 'data'),
              [Input('sun', 'selectedPath')])
def display_sun(selectedPath):
    print('->'.join(selectedPath))
    return create_data_from_path(selectedPath)


if __name__ == '__main__':
    app.run_server(debug=True)
