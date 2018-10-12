# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Sunburst(Component):
    """A Sunburst component.


Keyword arguments:
- id (string; optional): The ID used to identify this component in Dash callbacks
- width (number; optional): Dimensions of the figure to draw, in pixels
- height (number; optional)
- padding (number; optional): Pixels to leave blank around the edges
- innerRadius (number; optional): Radius, in pixels, for the inner circle when you're zoomed in,
that you click on to zoom back out
- transitionDuration (number; optional): Animation duration when you click around selecting subtrees
- data (dict; required): The sunburst data. Should have the form:

  `{name: '...', children: [c0, c1, c2]}`

and children `c<i>` can have the same form to arbitrary nesting,
or for leaf nodes the form is:

  `{name: '...', size: ###}`
- dataVersion (string | number; optional): Optional version id for data, to avoid having to diff a large object
- selectedPath (list; optional): The currently selected path within the sunburst
as an array of child names

Available events: """
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, padding=Component.UNDEFINED, innerRadius=Component.UNDEFINED, transitionDuration=Component.UNDEFINED, data=Component.REQUIRED, dataVersion=Component.UNDEFINED, selectedPath=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'width', 'height', 'padding', 'innerRadius', 'transitionDuration', 'data', 'dataVersion', 'selectedPath']
        self._type = 'Sunburst'
        self._namespace = 'dash_sunburst'
        self._valid_wildcard_attributes =            []
        self.available_events = []
        self.available_properties = ['id', 'width', 'height', 'padding', 'innerRadius', 'transitionDuration', 'data', 'dataVersion', 'selectedPath']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in [u'data']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Sunburst, self).__init__(**args)

    def __repr__(self):
        if(any(getattr(self, c, None) is not None
               for c in self._prop_names
               if c is not self._prop_names[0])
           or any(getattr(self, c, None) is not None
                  for c in self.__dict__.keys()
                  if any(c.startswith(wc_attr)
                  for wc_attr in self._valid_wildcard_attributes))):
            props_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self._prop_names
                                      if getattr(self, c, None) is not None])
            wilds_string = ', '.join([c+'='+repr(getattr(self, c, None))
                                      for c in self.__dict__.keys()
                                      if any([c.startswith(wc_attr)
                                      for wc_attr in
                                      self._valid_wildcard_attributes])])
            return ('Sunburst(' + props_string +
                   (', ' + wilds_string if wilds_string != '' else '') + ')')
        else:
            return (
                'Sunburst(' +
                repr(getattr(self, self._prop_names[0], None)) + ')')
