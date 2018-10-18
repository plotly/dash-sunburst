import React, {Component} from 'react';
import PropTypes from 'prop-types';
import SunburstD3 from '../d3/sunburst';

export default class Sunburst extends Component {
    constructor(props) {
        super(props);
        this.create = this.create.bind(this);
    }

    componentDidMount() {
        this.create();
    }

    componentDidUpdate(prevProps) {
        if (this.props.updatemode === 'replace') {
            if (JSON.stringify(this.props) !== JSON.stringify(prevProps)) {
                this.el.innerHTML = '';
                this.create();
            }
        } else {
            this.sunburst.update(this.props);
        }
    }

    create() {
        this.sunburst = new SunburstD3(this.el, this.props, figure => {
           const {setProps} = this.props;
           const {selectedPath} = figure;

           if (setProps) { setProps({selectedPath}); }
           else { this.setState({selectedPath}); }
       });
    }

    render() {
        return <div id={this.props.id} ref={el => {this.el = el}} />;
    }
}


Sunburst.defaultProps = {
    updatemode: 'animate'
};


Sunburst.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks
     */
    id: PropTypes.string,

    /**
     * Dash-assigned callback that should be called whenever any of the
     * properties change
     */
    setProps: PropTypes.func,

    /**
     * Width of the figure to draw, in pixels
     */
    width: PropTypes.number,

    /**
     * Height of the figure to draw, in pixels
     */
    height: PropTypes.number,

    /**
     * Pixels to leave blank around the edges
     */
    padding: PropTypes.number,

    /**
     * Radius, in pixels, for the inner circle when you're zoomed in,
     * that you click on to zoom back out
     */
    innerRadius: PropTypes.number,

    /**
     * Animation duration when you click around selecting subtrees
     */
    transitionDuration: PropTypes.number,

    /**
     * The sunburst data. Should have the form:
     *
     *   `{name: '...', children: [c0, c1, c2]}`
     *
     * and children `c<i>` can have the same form to arbitrary nesting,
     * or for leaf nodes the form is:
     *
     *   `{name: '...', size: ###}`
     *
     * any node can also have a `color` property, set to any CSS color string,
     * to use instead of the default coloring. Nodes with no children will
     * inherit their parent's color if not specified. Otherwise colors are pulled
     * from d3.scale.category20 in the order nodes are encountered.
     */
    data: PropTypes.object.isRequired,

    /**
     * Optional version id for data, to avoid having to diff a large object
     */
    dataVersion: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),

    /**
     * The currently selected path within the sunburst
     * as an array of child names
     */
    selectedPath: PropTypes.arrayOf(PropTypes.string),

    /**
     * If 'replace', then the graph is completely replaced on updates
     * if 'animate', then the graph tweens between updates.
     * Use 'replace' if you are generating data server side
     */
    updatemode: PropTypes.oneOf(['replace', 'animate'])
};
