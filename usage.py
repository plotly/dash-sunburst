import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from dash_sunburst import Sunburst

app = dash.Dash('')

app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

sunburst_data = {
    'name': 'house',
    'children': [
        {
            'name': 'living room',
            'children': [
                {'name': 'couch', 'size': 6},
                {'name': 'tv', 'size': 3},
                {'name': 'desk', 'size': 4},
                {'name': 'chair', 'size': 1},
                {'name': 'table', 'size': 5},
                {'name': 'piano', 'size': 2}
            ]
        },
        {
            'name': 'kitchen',
            'children': [
                {'name': 'fridge', 'size': 3.5},
                {'name': 'dishwasher', 'size': 2.5},
                {'name': 'sink', 'size': 1.5},
                {'name': 'cabinets', 'size': 8},
                {'name': 'oven', 'size': 1.7}
            ]
        },
        {'name': 'coat closet', 'size': 4.5},
        {'name': 'storage closet', 'size': 10},
        {'name': 'bathroom', 'size': 7.5},
        {
            'name': 'master bedroom',
            'children': [
                {'name': 'bed', 'size': 9},
                {'name': 'recliner', 'size': 3.2},
                {'name': 'dresser', 'size': 4.7},
                {'name': 'master bath', 'size': 7},
                {'name': 'closet', 'size': 5.5}
            ]
        },
        {
            'name': 'bedroom',
            'children': [
                {'name': 'bed', 'size': 5.7},
                {'name': 'desk', 'size': 3.8},
                {'name': 'dresser', 'size': 4.7},
                {'name': 'closet', 'size': 5.3}
            ]
        },
        {'name': 'hall', 'size': 11}
    ]
}

app.layout = html.Div([
    html.Div(
        [Sunburst(id='sun', data=sunburst_data)],
        style={'width': '49%', 'display': 'inline-block', 'float': 'left'}),
    dcc.Graph(
        id='graph',
        style={'width': '49%', 'display': 'inline-block', 'float': 'left'}),
    html.Div(id='output', style={'clear': 'both'})
])

@app.callback(Output('output', 'children'), [Input('sun', 'selectedPath')])
def display_selected(selected_path):
    return 'You have selected path: {}'.format('->'.join(selected_path or []) or 'root')

@app.callback(Output('graph', 'figure'), [Input('sun', 'data'), Input('sun', 'selectedPath')])
def display_graph(data, selected_path):
    x = []
    y = []
    text = []
    color = []
    joined_selected = '->'.join(selected_path or [])

    SELECTED_COLOR = '#03c'
    SELECTED_CHILDREN_COLOR = '#8cf'
    SELECTED_PARENTS_COLOR = '#f80'
    DESELECTED_COLOR = '#ccc'

    def node_color(node_path):
        joined_node = '->'.join(node_path)
        if joined_node == joined_selected:
            return SELECTED_COLOR
        if joined_node.startswith(joined_selected):
            return SELECTED_CHILDREN_COLOR
        if joined_selected.startswith(joined_node):
            return SELECTED_PARENTS_COLOR
        return DESELECTED_COLOR

    def append_point(child_count, size, node, node_path):
        x.append(child_count)
        y.append(size)
        text.append(node['name'])
        color.append(node_color(node_path))

    def crawl(node, node_path):
        if 'size' in node:
            append_point(1, node['size'], node, node_path)
            return (1, node['size'])
        else:
            node_count, node_size = 1, 0
            for child in node['children']:
                this_count, this_size = crawl(child, node_path + [child['name']])
                node_count += this_count
                node_size += this_size
            append_point(node_count, node_size, node, node_path)
            return (node_count, node_size)

    crawl(data, [])

    layout = {
        'width': 500,
        'height': 500,
        'xaxis': {'title': 'Total Nodes', 'type': 'log'},
        'yaxis': {'title': 'Total Size', 'type': 'log'},
        'hovermode': 'closest'
    }

    return {
        'data': [{
            'x': x,
            'y': y,
            'text': text,
            'textposition': 'middle right',
            'marker': {
                'color': color,
                'size': [(v*v + 100)**0.5 for v in y],
                'opacity': 0.5
            },
            'mode': 'markers+text',
            'cliponaxis': False
        }],
        'layout': layout
    }

if __name__ == '__main__':
    app.run_server(debug=True)
