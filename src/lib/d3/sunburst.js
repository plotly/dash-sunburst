import d3 from 'd3';

const dflts = {
    width: 600,
    height: 500,
    padding: 10,
    innerRadius: 20,
    transitionDuration: 750
};

const numFormat = d3.format(',.3g');

const Tau = 2 * Math.PI;

function constrain(v, vMin, vMax) {
    return Math.max(vMin, Math.min(vMax, v));
}

const textStyle = {
    fill: '#444',
    'text-anchor': 'middle',
    'font-size': '10px',
    'font-family': 'Arial',
    'text-shadow': 'white -1px 0px 0.5px, white 0px -1px 0.5px, white 0px 1px 0.5px, white 1px 0px 0.5px'
};

export default class SunburstD3 {
    constructor(el, figure, onChange) {
        const self = this;
        self.update = self.update.bind(self);
        self._update = self._update.bind(self);

        self.svg = d3.select(el).append('svg');
        self.pathGroup = self.svg.append('g');
        self.textGroup = self.svg.append('g')
            .style('pointer-events', 'none');

        self.angularScale = d3.scale.linear().range([0, Tau]);
        self.radialScale = d3.scale.sqrt();
        self.colorScale = d3.scale.category20();
        self.partition = d3.layout.partition()
            .value(d => !d.children && d.size)
            .sort((a, b) => a.i - b.i);

        self.arc = d3.svg.arc()
            .startAngle(d => constrain(self.angularScale(d.x), 0, Tau))
            .endAngle(d => constrain(self.angularScale(d.x + d.dx), 0, Tau))
            .innerRadius(d => Math.max(0, self.radialScale(d.y)))
            .outerRadius(d => Math.max(0, self.radialScale(d.y + d.dy)));

        self.figure = {};

        self.onChange = onChange;

        self.initialized = false;

        self._promise = Promise.resolve();

        self.update(figure);
    }

    update(figure) {
        const self = this;
        // ensure any previous transition is complete before we start
        self._promise = self._promise.then(() => self._update(figure));
    }

    _update(figure) {
        const self = this;
        const oldFigure = self.figure;

        // fill defaults in the new figure
        const width = figure.width || dflts.width;
        const height = figure.height || dflts.height;
        // interactive: undefined defaults to true
        const interactive = figure.interactive !== false;
        const padding = figure.padding || dflts.padding;
        const innerRadius = figure.innerRadius || dflts.innerRadius;
        const transitionDuration = figure.transitionDuration || dflts.transitionDuration;
        const {data, dataVersion} = figure;
        const selectedPath = figure.selectedPath || [];

        const newFigure = self.figure = {
            width,
            height,
            interactive,
            padding,
            innerRadius,
            transitionDuration,
            data,
            dataVersion,
            selectedPath
        };

        /*
         * Definitions
         */

        const selectedX = node => [node.x, node.x + node.dx];
        const selectedY = node => [node.y, 1];
        const selectedRadius = node => [node.y ? self.figure.innerRadius : 0, self.radius];

        const rCenter = node => self.radialScale(node.y + node.dy / 2);
        const angleCenter = node => self.angularScale(node.x + node.dx / 2);
        const xCenter = node => rCenter(node) * Math.sin(angleCenter(node));
        const yCenter = node => -rCenter(node) * Math.cos(angleCenter(node));

        const skinny = node => {
            const dtheta = self.angularScale(node.x + node.dx) - self.angularScale(node.x);
            const r0 = self.radialScale(node.y);
            const dr = self.radialScale(node.y + node.dy) / r0 - 1;
            return r0 && (dr / dtheta > 1);
        };

        const textTrans = node => {
            const rot = (angleCenter(node) * 360 / Tau + (skinny(node) ? 0 : 90)) % 180 - 90;
            return 'rotate(' + rot + ',' + xCenter(node) + ',' + yCenter(node) + ')';
        };

        const hideText = node => {
            return (
                angleCenter(node) > 0 && angleCenter(node) < Tau &&
                rCenter(node) > 0 && rCenter(node) < self.radius
            ) ? 1 : 0;
        }

        const posOnly = (d) => {
            const {x, dx, y, dy} = d;
            return {x, dx, y, dy};
        }

        function wrap(accessor) {
            return d => {
                return t => {
                    const d0 = self.oldDataMap[getPathStr(d)];
                    if(d0 && d0 !== d) {
                        const interpolator = d3.interpolateObject(posOnly(d0), posOnly(d));
                        return accessor(interpolator(t));
                    }
                    return accessor(d);
                }
            };
        }

        const transitionToNode = node => {
            // simultaneous transitions can cause infinite loops in some cases
            // mostly self._promise takes care of this, we want to avoid clicks
            // during transitions.
            self.transitioning = true;
            const transition = self.svg.transition()
                .duration(self.figure.transitionDuration)
                .tween('scale', () => {
                    const angularDomain = d3.interpolate(
                        self.angularScale.domain(),
                        selectedX(node)
                    );
                    const radialDomain = d3.interpolate(
                        self.radialScale.domain(),
                        selectedY(node)
                    );
                    const radialRange = d3.interpolate(
                        self.radialScale.range(),
                        selectedRadius(node)
                    );
                    return function(t) {
                        self.angularScale
                            .domain(angularDomain(t));
                        self.radialScale
                            .domain(radialDomain(t))
                            .range(radialRange(t));
                    };
                });
            transition.selectAll('path')
                .attrTween('d', wrap(self.arc));
            transition.selectAll('text')
                .attrTween('x', wrap(xCenter))
                .attrTween('y', wrap(yCenter))
                .attrTween('transform', wrap(textTrans))
                .attrTween('opacity', wrap(hideText));

            if(self.onChange) {
                self.figure.selectedPath = getPath(node);
                self.onChange(self.figure);
            }
            return transition;
        };

        const updatePaths = (_paths, _texts, _dataChange) => {
            if(_dataChange) {
                const enteringPaths = _paths.enter().append('path')
                    .style({stroke: '#fff', strokeWidth: 1})
                    .on('click', node => {
                        if(self.transitioning) { return; }
                        self._promise = self._promise.then(() => {
                            return new Promise(resolve => {
                                if(self.figure.interactive) {
                                    transitionToNode(node)
                                        .each('end', () => {
                                            self.transitioning = false;
                                            resolve();
                                        });
                                }
                                else {
                                    resolve();
                                }
                            });
                        });
                    });
                enteringPaths.append('title');

                _texts.enter().append('text')
                    .style(textStyle)
                    .text(d => d.name);
            }

            /*
             * Updates to attributes, that we need to do regardless of what changed
             */

            _paths
                .attr('d', self.arc)
                // coloring this way will be history-dependent: if you insert a
                // new item in the middle it will get the next color, and existing
                // items will keep their colors. But if you later redraw this
                // component straight from the final data you'll get different colors
                .style('fill', d => (
                    // first look for an explicit color (or explicit parent color)
                    d.color ||
                    (!d.children && d.parent.color) ||
                    self.colorScale(getPathStr(d.children ? d : d.parent))
                ));

            // title is a cheap solution for tooltips; better is to call
            // `d3.on('mouse(over|out)')` and draw a tooltip.
            // That requires a bit of extra logic if you want these tooltips
            // to work correctly across state updates
            _paths.select('title').text(d => d.name + '\n' + numFormat(d.value));

            _texts
                .attr('x', xCenter)
                .attr('y', yCenter)
                .attr('transform', textTrans)
                .attr('opacity', hideText);

            const dataMap = self.oldDataMap = {};
            _paths.each(d => {
                dataMap[getPathStr(d)] = posOnly(d);
            });
        };

        const setSize = () => {
            self.radius = (Math.min(height, width) / 2) - padding;

            self.svg.attr({width, height});
            const centered = 'translate(' + (width / 2) + ',' + (height / 2) + ')';
            self.pathGroup.attr('transform', centered);
            self.textGroup.attr('transform', centered);
        };

        /*
         * Diffing
         */

        let retVal = Promise.resolve();

        const change = diff(oldFigure, newFigure);
        if(!change) { return retVal; }

        const sizeChange = change.width || change.height || change.padding;
        const dataChange = change.data;

        const oldRootName = self.rootName;
        const newRootName = self.rootName = data.name;

        const oldSelectedPath = self.selectedPath;
        const newSelectedPath = self.selectedPath = selectedPath.slice();

        /*
         * Drawing
         */

        if(sizeChange) { setSize(); }

        let paths = self.pathGroup.selectAll('path');
        let texts = self.textGroup.selectAll('text');

        if(dataChange) {
            // clone data before partitioning, since this mutates the data
            self.nodes = self.partition.nodes(addIndices(JSON.parse(JSON.stringify(data))));
            paths = paths.data(self.nodes, getPathStr);
            texts = texts.data(self.nodes, getPathStr);

            // exit paths at the beginning of the transition
            // enters will happen at the end
            paths.exit().remove();
            texts.exit().remove();
        }

        const selectedNode = getNode(self.nodes[0], selectedPath);
        // no node: path is wrong, probably because we received a new selectedPath
        // before the data it belongs with
        if(!selectedNode) { return retVal; }

        // immediate redraw rather than transition if:
        const shouldAnimate =
            // first draw
            self.initialized &&
            // new root node
            (newRootName === oldRootName) &&
            // not a pure up/down transition
            sameHead(oldSelectedPath, newSelectedPath) &&
            // the previous data didn't contain the new selected node
            // this can happen if we transition selectedPath first, then data
            (!dataChange || getNode(oldFigure.data, newSelectedPath));

        console.log(shouldAnimate, oldSelectedPath, newSelectedPath);

        if(shouldAnimate) {
            retVal = new Promise(resolve => {
                transitionToNode(selectedNode)
                    .each('end', () => {
                        updatePaths(paths, texts, dataChange);
                        self.transitioning = false;
                        resolve();
                    });
            });
        }
        else {
            // first draw has no animation, and initializes the scales
            self.angularScale.domain(selectedX(selectedNode));
            self.radialScale.domain(selectedY(selectedNode))
            self.radialScale.range(selectedRadius(selectedNode));

            updatePaths(paths, texts, dataChange);

            self.initialized = true;
        }
        return retVal;
    }
};

function sameHead(array1, array2) {
    const len = Math.min(array1.length, array2.length);
    for(let i = 0; i < len; i++) {
        if(array1[i] !== array2[i]) { return false; }
    }
    return true;
}

// so we can sort by index, not by size as partition does by default.
function addIndices(node) {
    if(node.children) {
        node.children.forEach((child, i) => {
            child.i = i;
            addIndices(child);
        });
    }
    return node;
}

function getPath(d) {
    return d.parent ? getPath(d.parent).concat([d.name]) : [];
}

function getPathStr(d) {
    return getPath(d).join(',') || d.name;
}

function getNode(node, path) {
    if(!path.length) { return node; }
    if(!node.children) { return false; }

    let childi;
    for(var i = 0; i < node.children.length; i++) {
        childi = node.children[i];
        if(childi.name === path[0]) {
            return getNode(childi, path.slice(1));
        }
    }
    return false;
}

/**
 * Very simple diff - assumes newObj is flat and has all the possible keys from oldObj
 * uses a "dataVersion" key to avoid diffing the full data object.
 * In fact, this way we can avoid copying data (ie treating it immutably),
 * and just use dataVersion to track mutations.
 */
function diff(oldObj, newObj) {
    const V = 'Version';
    const out = {};
    let hasChange = false;
    for(const key in newObj) {
        if(key.substr(key.length - V.length) === V) { continue; }

        if(typeof newObj[key] === 'object') {
            if(newObj[key + V]) {
                if(newObj[key + V] !== oldObj[key + V]) {
                    out[key] = 1;
                    hasChange = true;
                }
            }
            else if(JSON.stringify(oldObj[key]) !== JSON.stringify(newObj[key])) {
                out[key] = 1;
                hasChange = true;
            }
        }
        else if(oldObj[key] !== newObj[key]) {
            out[key] = 1;
            hasChange = true;
        }
    }
    return hasChange && out;
}
