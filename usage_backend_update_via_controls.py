import dash
from dash.dependencies import Input, Output
import dash_sunburst
import dash_core_components as dcc
import dash_html_components as html


N_CHILDREN = 3

def node_name(level_index, node_index):
    return 'Level {}, Node {}'.format(level_index, node_index)

def create_data(start_level_index, node_index):
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
    for i in range(start_level_index - 1, 0, -1):
        data = {
            'name': node_name(i, 1),
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
        interactive=False # disable clicking nodes
    )
])


@app.callback(Output('node', 'options'), [Input('level', 'value')])
def update_node_options(level):
    # first level only has one node
    level_nodes = N_CHILDREN if level > 1 else 1
    return [{
        'label': 'Level {}, Node {}'.format(level, i),
        'value': i
    } for i in range(1, level_nodes + 1)]


@app.callback(Output('node', 'value'), [Input('node', 'options')])
def update_node_value(options):
    return options[0]['value']

# Originally I had both sun.selectedPath and sun.data depend on
# level.value and node.value. But the two callbacks would fire separately and
# in random order, which confused the receiving component.
#
# In order to ensure a consistent order of operations, I have selectedPath
# depend on level and node, and then data depends on selectedPath.
@app.callback(Output('sun', 'selectedPath'), [
    Input('level', 'value'),
    Input('node', 'value')])
def update_selected_path(level, node):
    path = [node_name(i, node if i == level else 1) for i in range(2, level + 1)]
    return path


@app.callback(Output('sun', 'data'), [Input('sun', 'selectedPath')])
def update_sun(selectedPath):
    if(len(selectedPath)):
        (level, node) = extract_level_and_node_from_name(selectedPath[-1])
    else:
        (level, node) = (1, 1)
    return create_data(level, node)


if __name__ == '__main__':
    app.run_server(debug=True)
