(function(){

var nv = window.nv || {};


nv.version = '1.1.15b';
nv.dev = true //set false when in production

window.nv = nv;

nv.tooltip = nv.tooltip || {}; // For the tooltip system
nv.utils = nv.utils || {}; // Utility subsystem
nv.models = nv.models || {}; //stores all the possible models/components
nv.charts = {}; //stores all the ready to use charts
nv.graphs = []; //stores all the graphs currently on the page
nv.logs = {}; //stores some statistics and potential error messages

nv.dispatch = d3.dispatch('render_start', 'render_end');

// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};
// *************************************************************************
//  Development render timers - disabled if dev = false

if (nv.dev) {
  nv.dispatch.on('render_start', function(e) {
    nv.logs.startTime = +new Date();
  });

  nv.dispatch.on('render_end', function(e) {
    nv.logs.endTime = +new Date();
    nv.logs.totalTime = nv.logs.endTime - nv.logs.startTime;
    nv.log('total', nv.logs.totalTime); // used for development, to keep track of graph generation times
  });
}

// ********************************************
//  Public Core NV functions

// Logs all arguments, and returns the last so you can test things in place
// Note: in IE8 console.log is an object not a function, and if modernizr is used
// then calling Function.prototype.bind with with anything other than a function
// causes a TypeError to be thrown.
nv.log = function() {
  if (nv.dev && console.log && console.log.apply)
    console.log.apply(console, arguments)
  else if (nv.dev && typeof console.log == "function" && Function.prototype.bind) {
    var log = Function.prototype.bind.call(console.log, console);
    log.apply(console, arguments);
  }
  return arguments[arguments.length - 1];
};


nv.render = function render(step) {
  step = step || 1; // number of graphs to generate in each timeout loop

  nv.render.active = true;
  nv.dispatch.render_start();

  setTimeout(function() {
    var chart, graph;

    for (var i = 0; i < step && (graph = nv.render.queue[i]); i++) {
      chart = graph.generate();
      if (typeof graph.callback == typeof(Function)) graph.callback(chart);
      nv.graphs.push(chart);
    }

    nv.render.queue.splice(0, i);

    if (nv.render.queue.length) setTimeout(arguments.callee, 0);
    else {
      nv.dispatch.render_end();
      nv.render.active = false;
    }
  }, 0);
};

nv.render.active = false;
nv.render.queue = [];

nv.addGraph = function(obj) {
  if (typeof arguments[0] === typeof(Function))
    obj = {generate: arguments[0], callback: arguments[1]};

  nv.render.queue.push(obj);

  if (!nv.render.active) nv.render();
};

nv.identity = function(d) { return d; };

nv.strip = function(s) { return s.replace(/(\s|&)/g,''); };

function daysInMonth(month,year) {
  return (new Date(year, month+1, 0)).getDate();
}

function d3_time_range(floor, step, number) {
  return function(t0, t1, dt) {
    var time = floor(t0), times = [];
    if (time < t0) step(time);
    if (dt > 1) {
      while (time < t1) {
        var date = new Date(+time);
        if ((number(date) % dt === 0)) times.push(date);
        step(time);
      }
    } else {
      while (time < t1) { times.push(new Date(+time)); step(time); }
    }
    return times;
  };
}

d3.time.monthEnd = function(date) {
  return new Date(date.getFullYear(), date.getMonth(), 0);
};

d3.time.monthEnds = d3_time_range(d3.time.monthEnd, function(date) {
    date.setUTCDate(date.getUTCDate() + 1);
    date.setDate(daysInMonth(date.getMonth() + 1, date.getFullYear()));
  }, function(date) {
    return date.getMonth();
  }
);

/* Utility class to handle creation of an interactive layer.
This places a rectangle on top of the chart. When you mouse move over it, it sends a dispatch
containing the X-coordinate. It can also render a vertical line where the mouse is located.

dispatch.elementMousemove is the important event to latch onto.  It is fired whenever the mouse moves over
the rectangle. The dispatch is given one object which contains the mouseX/Y location.
It also has 'pointXValue', which is the conversion of mouseX to the x-axis scale.
*/
nv.interactiveGuideline = function() {
    "use strict";
    var tooltip = nv.models.tooltip();
    //Public settings
    var width = null
    , height = null
    //Please pass in the bounding chart's top and left margins
    //This is important for calculating the correct mouseX/Y positions.
    , margin = {left: 0, top: 0}
    , xScale = d3.scale.linear()
    , yScale = d3.scale.linear()
    , dispatch = d3.dispatch('elementMousemove', 'elementMouseout','elementDblclick')
    , showGuideLine = true
    , svgContainer = null
    //Must pass in the bounding chart's <svg> container.
    //The mousemove event is attached to this container.
    ;

    //Private variables
    var isMSIE = navigator.userAgent.indexOf("MSIE") !== -1  //Check user-agent for Microsoft Internet Explorer.
    ;


    function layer(selection) {
        selection.each(function(data) {
                var container = d3.select(this);

                var availableWidth = (width || 960), availableHeight = (height || 400);

                var wrap = container.selectAll("g.nv-wrap.nv-interactiveLineLayer").data([data]);
                var wrapEnter = wrap.enter()
                                .append("g").attr("class", " nv-wrap nv-interactiveLineLayer");


                wrapEnter.append("g").attr("class","nv-interactiveGuideLine");

                if (!svgContainer) {
                    return;
                }

                function mouseHandler() {
                      var d3mouse = d3.mouse(this);
                      var mouseX = d3mouse[0];
                      var mouseY = d3mouse[1];
                      var subtractMargin = true;
                      var mouseOutAnyReason = false;
                      if (isMSIE) {
                         /*
                            D3.js (or maybe SVG.getScreenCTM) has a nasty bug in Internet Explorer 10.
                            d3.mouse() returns incorrect X,Y mouse coordinates when mouse moving
                            over a rect in IE 10.
                            However, d3.event.offsetX/Y also returns the mouse coordinates
                            relative to the triggering <rect>. So we use offsetX/Y on IE.
                         */
                         mouseX = d3.event.offsetX;
                         mouseY = d3.event.offsetY;

                         /*
                            On IE, if you attach a mouse event listener to the <svg> container,
                            it will actually trigger it for all the child elements (like <path>, <circle>, etc).
                            When this happens on IE, the offsetX/Y is set to where ever the child element
                            is located.
                            As a result, we do NOT need to subtract margins to figure out the mouse X/Y
                            position under this scenario. Removing the line below *will* cause
                            the interactive layer to not work right on IE.
                         */
                         if(d3.event.target.tagName !== "svg")
                            subtractMargin = false;

                         if (d3.event.target.className.baseVal.match("nv-legend"))
                             mouseOutAnyReason = true;

                      }

                      if(subtractMargin) {
                         mouseX -= margin.left;
                         mouseY -= margin.top;
                      }

                      /* If mouseX/Y is outside of the chart's bounds,
                      trigger a mouseOut event.
                      */
                      if (mouseX < 0 || mouseY < 0
                        || mouseX > availableWidth || mouseY > availableHeight
                        || (d3.event.relatedTarget && d3.event.relatedTarget.ownerSVGElement === undefined)
                        || mouseOutAnyReason
                        )
                      {
                              if (isMSIE) {
                                  if (d3.event.relatedTarget
                                      && d3.event.relatedTarget.ownerSVGElement === undefined
                                      && d3.event.relatedTarget.className.match(tooltip.nvPointerEventsClass)) {
                                      return;
                                  }
                              }
                            dispatch.elementMouseout({
                               mouseX: mouseX,
                               mouseY: mouseY
                            });
                            layer.renderGuideLine(null); //hide the guideline
                            return;
                      }

                      var pointXValue = xScale.invert(mouseX);
                      dispatch.elementMousemove({
                            mouseX: mouseX,
                            mouseY: mouseY,
                            pointXValue: pointXValue
                      });

                      //If user double clicks the layer, fire a elementDblclick dispatch.
                      if (d3.event.type === "dblclick") {
                        dispatch.elementDblclick({
                            mouseX: mouseX,
                            mouseY: mouseY,
                            pointXValue: pointXValue
                        });
                      }
                }

                svgContainer
                      .on("mousemove",mouseHandler, true)
                      .on("mouseout" ,mouseHandler,true)
                      .on("dblclick" ,mouseHandler)
                      ;

                 //Draws a vertical guideline at the given X postion.
                layer.renderGuideLine = function(x) {
                     if (!showGuideLine) return;
                     var line = wrap.select(".nv-interactiveGuideLine")
                           .selectAll("line")
                           .data((x != null) ? [nv.utils.NaNtoZero(x)] : [], String);

                     line.enter()
                         .append("line")
                         .attr("class", "nv-guideline")
                         .attr("x1", function(d) { return d;})
                         .attr("x2", function(d) { return d;})
                         .attr("y1", availableHeight)
                         .attr("y2",0)
                         ;
                     line.exit().remove();

                }
        });
    }

    layer.dispatch = dispatch;
    layer.tooltip = tooltip;

    layer.margin = function(_) {
        if (!arguments.length) return margin;
        margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
        margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
        return layer;
    };

    layer.width = function(_) {
        if (!arguments.length) return width;
        width = _;
        return layer;
    };

    layer.height = function(_) {
        if (!arguments.length) return height;
        height = _;
        return layer;
    };

    layer.xScale = function(_) {
        if (!arguments.length) return xScale;
        xScale = _;
        return layer;
    };

    layer.showGuideLine = function(_) {
        if (!arguments.length) return showGuideLine;
        showGuideLine = _;
        return layer;
    };

    layer.svgContainer = function(_) {
        if (!arguments.length) return svgContainer;
        svgContainer = _;
        return layer;
    };


    return layer;
};

/* Utility class that uses d3.bisect to find the index in a given array, where a search value can be inserted.
This is different from normal bisectLeft; this function finds the nearest index to insert the search value.

For instance, lets say your array is [1,2,3,5,10,30], and you search for 28.
Normal d3.bisectLeft will return 4, because 28 is inserted after the number 10.  But interactiveBisect will return 5
because 28 is closer to 30 than 10.

Unit tests can be found in: interactiveBisectTest.html

Has the following known issues:
   * Will not work if the data points move backwards (ie, 10,9,8,7, etc) or if the data points are in random order.
   * Won't work if there are duplicate x coordinate values.
*/
nv.interactiveBisect = function (values, searchVal, xAccessor) {
      "use strict";
      if (! values instanceof Array) return null;
      if (typeof xAccessor !== 'function') xAccessor = function(d,i) { return d.x;}

      var bisect = d3.bisector(xAccessor).left;
      var index = d3.max([0, bisect(values,searchVal) - 1]);
      var currentValue = xAccessor(values[index], index);
      if (typeof currentValue === 'undefined') currentValue = index;

      if (currentValue === searchVal) return index;  //found exact match

      var nextIndex = d3.min([index+1, values.length - 1]);
      var nextValue = xAccessor(values[nextIndex], nextIndex);
      if (typeof nextValue === 'undefined') nextValue = nextIndex;

      if (Math.abs(nextValue - searchVal) >= Math.abs(currentValue - searchVal))
          return index;
      else
          return nextIndex
};

/*
Returns the index in the array "values" that is closest to searchVal.
Only returns an index if searchVal is within some "threshold".
Otherwise, returns null.
*/
nv.nearestValueIndex = function (values, searchVal, threshold) {
      "use strict";
      var yDistMax = Infinity, indexToHighlight = null;
      values.forEach(function(d,i) {
         var delta = Math.abs(searchVal - d);
         if ( delta <= yDistMax && delta < threshold) {
            yDistMax = delta;
            indexToHighlight = i;
         }
      });
      return indexToHighlight;
};/* Tooltip rendering model for nvd3 charts.
window.nv.models.tooltip is the updated,new way to render tooltips.

window.nv.tooltip.show is the old tooltip code.
window.nv.tooltip.* also has various helper methods.
*/
(function() {
  "use strict";
  window.nv.tooltip = {};

  /* Model which can be instantiated to handle tooltip rendering.
    Example usage:
    var tip = nv.models.tooltip().gravity('w').distance(23)
                .data(myDataObject);

        tip();    //just invoke the returned function to render tooltip.
  */
  window.nv.models.tooltip = function() {
        var content = null    //HTML contents of the tooltip.  If null, the content is generated via the data variable.
        ,   data = null     /* Tooltip data. If data is given in the proper format, a consistent tooltip is generated.
        Format of data:
        {
            key: "Date",
            value: "August 2009",
            series: [
                    {
                        key: "Series 1",
                        value: "Value 1",
                        color: "#000"
                    },
                    {
                        key: "Series 2",
                        value: "Value 2",
                        color: "#00f"
                    }
            ]

        }

        */
        ,   gravity = 'w'   //Can be 'n','s','e','w'. Determines how tooltip is positioned.
        ,   distance = 50   //Distance to offset tooltip from the mouse location.
        ,   snapDistance = 25   //Tolerance allowed before tooltip is moved from its current position (creates 'snapping' effect)
        ,   fixedTop = null //If not null, this fixes the top position of the tooltip.
        ,   classes = null  //Attaches additional CSS classes to the tooltip DIV that is created.
        ,   chartContainer = null   //Parent DIV, of the SVG Container that holds the chart.
        ,   tooltipElem = null  //actual DOM element representing the tooltip.
        ,   position = {left: null, top: null}      //Relative position of the tooltip inside chartContainer.
        ,   enabled = true  //True -> tooltips are rendered. False -> don't render tooltips.
        //Generates a unique id when you create a new tooltip() object
        ,   id = "nvtooltip-" + Math.floor(Math.random() * 100000)
        ;

        //CSS class to specify whether element should not have mouse events.
        var  nvPointerEventsClass = "nv-pointer-events-none";

        //Format function for the tooltip values column
        var valueFormatter = function(d,i) {
            return d;
        };

        //Format function for the tooltip header value.
        var headerFormatter = function(d) {
            return d;
        };

        //By default, the tooltip model renders a beautiful table inside a DIV.
        //You can override this function if a custom tooltip is desired.
        var contentGenerator = function(d) {
            if (content != null) return content;

            if (d == null) return '';

            var table = d3.select(document.createElement("table"));
            var theadEnter = table.selectAll("thead")
                .data([d])
                .enter().append("thead");
            theadEnter.append("tr")
                .append("td")
                .attr("colspan",3)
                .append("strong")
                    .classed("x-value",true)
                    .html(headerFormatter(d.value));

            var tbodyEnter = table.selectAll("tbody")
                .data([d])
                .enter().append("tbody");
            var trowEnter = tbodyEnter.selectAll("tr")
                .data(function(p) { return p.series})
                .enter()
                .append("tr")
                .classed("highlight", function(p) { return p.highlight})
                ;

            trowEnter.append("td")
                .classed("legend-color-guide",true)
                .append("div")
                    .style("background-color", function(p) { return p.color});
            trowEnter.append("td")
                .classed("key",true)
                .html(function(p) {return p.key});
            trowEnter.append("td")
                .classed("value",true)
                .html(function(p,i) { return valueFormatter(p.value,i) });


            trowEnter.selectAll("td").each(function(p) {
                if (p.highlight) {
                    var opacityScale = d3.scale.linear().domain([0,1]).range(["#fff",p.color]);
                    var opacity = 0.6;
                    d3.select(this)
                        .style("border-bottom-color", opacityScale(opacity))
                        .style("border-top-color", opacityScale(opacity))
                        ;
                }
            });

            var html = table.node().outerHTML;
            if (d.footer !== undefined)
                html += "<div class='footer'>" + d.footer + "</div>";
            return html;

        };

        var dataSeriesExists = function(d) {
            if (d && d.series && d.series.length > 0) return true;

            return false;
        };

        //In situations where the chart is in a 'viewBox', re-position the tooltip based on how far chart is zoomed.
        function convertViewBoxRatio() {
            if (chartContainer) {
              var svg = d3.select(chartContainer);
              if (svg.node().tagName !== "svg") {
                 svg = svg.select("svg");
              }
              var viewBox = (svg.node()) ? svg.attr('viewBox') : null;
              if (viewBox) {
                viewBox = viewBox.split(' ');
                var ratio = parseInt(svg.style('width')) / viewBox[2];

                position.left = position.left * ratio;
                position.top  = position.top * ratio;
              }
            }
        }

        //Creates new tooltip container, or uses existing one on DOM.
        function getTooltipContainer(newContent) {
            var body;
            if (chartContainer)
                body = d3.select(chartContainer);
            else
                body = d3.select("body");

            var container = body.select(".nvtooltip");
            if (container.node() === null) {
                //Create new tooltip div if it doesn't exist on DOM.
                container = body.append("div")
                    .attr("class", "nvtooltip " + (classes? classes: "xy-tooltip"))
                    .attr("id",id)
                    ;
            }


            container.node().innerHTML = newContent;
            container.style("top",0).style("left",0).style("opacity",0);
            container.selectAll("div, table, td, tr").classed(nvPointerEventsClass,true)
            container.classed(nvPointerEventsClass,true);
            return container.node();
        }



        //Draw the tooltip onto the DOM.
        function nvtooltip() {
            if (!enabled) return;
            if (!dataSeriesExists(data)) return;

            convertViewBoxRatio();

            var left = position.left;
            var top = (fixedTop != null) ? fixedTop : position.top;
            var container = getTooltipContainer(contentGenerator(data));
            tooltipElem = container;
            if (chartContainer) {
                var svgComp = chartContainer.getElementsByTagName("svg")[0];
                var boundRect = (svgComp) ? svgComp.getBoundingClientRect() : chartContainer.getBoundingClientRect();
                var svgOffset = {left:0,top:0};
                if (svgComp) {
                    var svgBound = svgComp.getBoundingClientRect();
                    var chartBound = chartContainer.getBoundingClientRect();
                    var svgBoundTop = svgBound.top;

                    //Defensive code. Sometimes, svgBoundTop can be a really negative
                    //  number, like -134254. That's a bug.
                    //  If such a number is found, use zero instead. FireFox bug only
                    if (svgBoundTop < 0) {
                        var containerBound = chartContainer.getBoundingClientRect();
                        svgBoundTop = (Math.abs(svgBoundTop) > containerBound.height) ? 0 : svgBoundTop;
                    }
                    svgOffset.top = Math.abs(svgBoundTop - chartBound.top);
                    svgOffset.left = Math.abs(svgBound.left - chartBound.left);
                }
                //If the parent container is an overflow <div> with scrollbars, subtract the scroll offsets.
                //You need to also add any offset between the <svg> element and its containing <div>
                //Finally, add any offset of the containing <div> on the whole page.
                left += chartContainer.offsetLeft + svgOffset.left - 2*chartContainer.scrollLeft;
                top += chartContainer.offsetTop + svgOffset.top - 2*chartContainer.scrollTop;
            }

            if (snapDistance && snapDistance > 0) {
                top = Math.floor(top/snapDistance) * snapDistance;
            }

            nv.tooltip.calcTooltipPosition([left,top], gravity, distance, container);
            return nvtooltip;
        };

        nvtooltip.nvPointerEventsClass = nvPointerEventsClass;

        nvtooltip.content = function(_) {
            if (!arguments.length) return content;
            content = _;
            return nvtooltip;
        };

        //Returns tooltipElem...not able to set it.
        nvtooltip.tooltipElem = function() {
            return tooltipElem;
        };

        nvtooltip.contentGenerator = function(_) {
            if (!arguments.length) return contentGenerator;
            if (typeof _ === 'function') {
                contentGenerator = _;
            }
            return nvtooltip;
        };

        nvtooltip.data = function(_) {
            if (!arguments.length) return data;
            data = _;
            return nvtooltip;
        };

        nvtooltip.gravity = function(_) {
            if (!arguments.length) return gravity;
            gravity = _;
            return nvtooltip;
        };

        nvtooltip.distance = function(_) {
            if (!arguments.length) return distance;
            distance = _;
            return nvtooltip;
        };

        nvtooltip.snapDistance = function(_) {
            if (!arguments.length) return snapDistance;
            snapDistance = _;
            return nvtooltip;
        };

        nvtooltip.classes = function(_) {
            if (!arguments.length) return classes;
            classes = _;
            return nvtooltip;
        };

        nvtooltip.chartContainer = function(_) {
            if (!arguments.length) return chartContainer;
            chartContainer = _;
            return nvtooltip;
        };

        nvtooltip.position = function(_) {
            if (!arguments.length) return position;
            position.left = (typeof _.left !== 'undefined') ? _.left : position.left;
            position.top = (typeof _.top !== 'undefined') ? _.top : position.top;
            return nvtooltip;
        };

        nvtooltip.fixedTop = function(_) {
            if (!arguments.length) return fixedTop;
            fixedTop = _;
            return nvtooltip;
        };

        nvtooltip.enabled = function(_) {
            if (!arguments.length) return enabled;
            enabled = _;
            return nvtooltip;
        };

        nvtooltip.valueFormatter = function(_) {
            if (!arguments.length) return valueFormatter;
            if (typeof _ === 'function') {
                valueFormatter = _;
            }
            return nvtooltip;
        };

        nvtooltip.headerFormatter = function(_) {
            if (!arguments.length) return headerFormatter;
            if (typeof _ === 'function') {
                headerFormatter = _;
            }
            return nvtooltip;
        };

        //id() is a read-only function. You can't use it to set the id.
        nvtooltip.id = function() {
            return id;
        };


        return nvtooltip;
  };


  //Original tooltip.show function. Kept for backward compatibility.
  // pos = [left,top]
  nv.tooltip.show = function(pos, content, gravity, dist, parentContainer, classes) {

        //Create new tooltip div if it doesn't exist on DOM.
        var   container = document.createElement('div');
        container.className = 'nvtooltip ' + (classes ? classes : 'xy-tooltip');

        var body = parentContainer;
        if ( !parentContainer || parentContainer.tagName.match(/g|svg/i)) {
            //If the parent element is an SVG element, place tooltip in the <body> element.
            body = document.getElementsByTagName('body')[0];
        }

        container.style.left = 0;
        container.style.top = 0;
        container.style.opacity = 0;
        container.innerHTML = content;
        body.appendChild(container);

        //If the parent container is an overflow <div> with scrollbars, subtract the scroll offsets.
        if (parentContainer) {
           pos[0] = pos[0] - parentContainer.scrollLeft;
           pos[1] = pos[1] - parentContainer.scrollTop;
        }
        nv.tooltip.calcTooltipPosition(pos, gravity, dist, container);
  };

  //Looks up the ancestry of a DOM element, and returns the first NON-svg node.
  nv.tooltip.findFirstNonSVGParent = function(Elem) {
            while(Elem.tagName.match(/^g|svg$/i) !== null) {
                Elem = Elem.parentNode;
            }
            return Elem;
  };

  //Finds the total offsetTop of a given DOM element.
  //Looks up the entire ancestry of an element, up to the first relatively positioned element.
  nv.tooltip.findTotalOffsetTop = function ( Elem, initialTop ) {
                var offsetTop = initialTop;

                do {
                    if( !isNaN( Elem.offsetTop ) ) {
                        offsetTop += (Elem.offsetTop);
                    }
                } while( Elem = Elem.offsetParent );
                return offsetTop;
  };

  //Finds the total offsetLeft of a given DOM element.
  //Looks up the entire ancestry of an element, up to the first relatively positioned element.
  nv.tooltip.findTotalOffsetLeft = function ( Elem, initialLeft) {
                var offsetLeft = initialLeft;

                do {
                    if( !isNaN( Elem.offsetLeft ) ) {
                        offsetLeft += (Elem.offsetLeft);
                    }
                } while( Elem = Elem.offsetParent );
                return offsetLeft;
  };

  //Global utility function to render a tooltip on the DOM.
  //pos = [left,top] coordinates of where to place the tooltip, relative to the SVG chart container.
  //gravity = how to orient the tooltip
  //dist = how far away from the mouse to place tooltip
  //container = tooltip DIV
  nv.tooltip.calcTooltipPosition = function(pos, gravity, dist, container) {

            var height = parseInt(container.offsetHeight),
                width = parseInt(container.offsetWidth),
                windowWidth = nv.utils.windowSize().width,
                windowHeight = nv.utils.windowSize().height,
                scrollTop = window.pageYOffset,
                scrollLeft = window.pageXOffset,
                left, top;

            windowHeight = window.innerWidth >= document.body.scrollWidth ? windowHeight : windowHeight - 16;
            windowWidth = window.innerHeight >= document.body.scrollHeight ? windowWidth : windowWidth - 16;

            gravity = gravity || 's';
            dist = dist || 20;

            var tooltipTop = function ( Elem ) {
                return nv.tooltip.findTotalOffsetTop(Elem, top);
            };

            var tooltipLeft = function ( Elem ) {
                return nv.tooltip.findTotalOffsetLeft(Elem,left);
            };

            switch (gravity) {
              case 'e':
                left = pos[0] - width - dist;
                top = pos[1] - (height / 2);
                var tLeft = tooltipLeft(container);
                var tTop = tooltipTop(container);
                if (tLeft < scrollLeft) left = pos[0] + dist > scrollLeft ? pos[0] + dist : scrollLeft - tLeft + left;
                if (tTop < scrollTop) top = scrollTop - tTop + top;
                if (tTop + height > scrollTop + windowHeight) top = scrollTop + windowHeight - tTop + top - height;
                break;
              case 'w':
                left = pos[0] + dist;
                top = pos[1] - (height / 2);
                var tLeft = tooltipLeft(container);
                var tTop = tooltipTop(container);
                if (tLeft + width > windowWidth) left = pos[0] - width - dist;
                if (tTop < scrollTop) top = scrollTop + 5;
                if (tTop + height > scrollTop + windowHeight) top = scrollTop + windowHeight - tTop + top - height;
                break;
              case 'n':
                left = pos[0] - (width / 2) - 5;
                top = pos[1] + dist;
                var tLeft = tooltipLeft(container);
                var tTop = tooltipTop(container);
                if (tLeft < scrollLeft) left = scrollLeft + 5;
                if (tLeft + width > windowWidth) left = left - width/2 + 5;
                if (tTop + height > scrollTop + windowHeight) top = scrollTop + windowHeight - tTop + top - height;
                break;
              case 's':
                left = pos[0] - (width / 2);
                top = pos[1] - height - dist;
                var tLeft = tooltipLeft(container);
                var tTop = tooltipTop(container);
                if (tLeft < scrollLeft) left = scrollLeft + 5;
                if (tLeft + width > windowWidth) left = left - width/2 + 5;
                if (scrollTop > tTop) top = scrollTop;
                break;
              case 'none':
                left = pos[0];
                top = pos[1] - dist;
                var tLeft = tooltipLeft(container);
                var tTop = tooltipTop(container);
                break;
            }


            container.style.left = left+'px';
            container.style.top = top+'px';
            container.style.opacity = 1;
            container.style.position = 'absolute';

            return container;
    };

    //Global utility function to remove tooltips from the DOM.
    nv.tooltip.cleanup = function() {

              // Find the tooltips, mark them for removal by this class (so others cleanups won't find it)
              var tooltips = document.getElementsByClassName('nvtooltip');
              var purging = [];
              while(tooltips.length) {
                purging.push(tooltips[0]);
                tooltips[0].style.transitionDelay = '0 !important';
                tooltips[0].style.opacity = 0;
                tooltips[0].className = 'nvtooltip-pending-removal';
              }

              setTimeout(function() {

                  while (purging.length) {
                     var removeMe = purging.pop();
                      removeMe.parentNode.removeChild(removeMe);
                  }
            }, 500);
    };

})();

nv.utils.windowSize = function() {
    // Sane defaults
    var size = {width: 640, height: 480};

    // Earlier IE uses Doc.body
    if (document.body && document.body.offsetWidth) {
        size.width = document.body.offsetWidth;
        size.height = document.body.offsetHeight;
    }

    // IE can use depending on mode it is in
    if (document.compatMode=='CSS1Compat' &&
        document.documentElement &&
        document.documentElement.offsetWidth ) {
        size.width = document.documentElement.offsetWidth;
        size.height = document.documentElement.offsetHeight;
    }

    // Most recent browsers use
    if (window.innerWidth && window.innerHeight) {
        size.width = window.innerWidth;
        size.height = window.innerHeight;
    }
    return (size);
};



// Easy way to bind multiple functions to window.onresize
// TODO: give a way to remove a function after its bound, other than removing all of them
nv.utils.windowResize = function(fun){
  if (fun === undefined) return;
  var oldresize = window.onresize;

  window.onresize = function(e) {
    if (typeof oldresize == 'function') oldresize(e);
    fun(e);
  }
}

// Backwards compatible way to implement more d3-like coloring of graphs.
// If passed an array, wrap it in a function which implements the old default
// behavior
nv.utils.getColor = function(color) {
    if (!arguments.length) return nv.utils.defaultColor(); //if you pass in nothing, get default colors back

    if( Object.prototype.toString.call( color ) === '[object Array]' )
        return function(d, i) { return d.color || color[i % color.length]; };
    else
        return color;
        //can't really help it if someone passes rubbish as color
}

// Default color chooser uses the index of an object as before.
nv.utils.defaultColor = function() {
    var colors = d3.scale.category20().range();
    return function(d, i) { return d.color || colors[i % colors.length] };
}


// Returns a color function that takes the result of 'getKey' for each series and
// looks for a corresponding color from the dictionary,
nv.utils.customTheme = function(dictionary, getKey, defaultColors) {
  getKey = getKey || function(series) { return series.key }; // use default series.key if getKey is undefined
  defaultColors = defaultColors || d3.scale.category20().range(); //default color function

  var defIndex = defaultColors.length; //current default color (going in reverse)

  return function(series, index) {
    var key = getKey(series);

    if (!defIndex) defIndex = defaultColors.length; //used all the default colors, start over

    if (typeof dictionary[key] !== "undefined")
      return (typeof dictionary[key] === "function") ? dictionary[key]() : dictionary[key];
    else
      return defaultColors[--defIndex]; // no match in dictionary, use default color
  }
}



// From the PJAX example on d3js.org, while this is not really directly needed
// it's a very cool method for doing pjax, I may expand upon it a little bit,
// open to suggestions on anything that may be useful
nv.utils.pjax = function(links, content) {
  d3.selectAll(links).on("click", function() {
    history.pushState(this.href, this.textContent, this.href);
    load(this.href);
    d3.event.preventDefault();
  });

  function load(href) {
    d3.html(href, function(fragment) {
      var target = d3.select(content).node();
      target.parentNode.replaceChild(d3.select(fragment).select(content).node(), target);
      nv.utils.pjax(links, content);
    });
  }

  d3.select(window).on("popstate", function() {
    if (d3.event.state) load(d3.event.state);
  });
}

/* For situations where we want to approximate the width in pixels for an SVG:text element.
Most common instance is when the element is in a display:none; container.
Forumla is : text.length * font-size * constant_factor
*/
nv.utils.calcApproxTextWidth = function (svgTextElem) {
    if (typeof svgTextElem.style === 'function'
        && typeof svgTextElem.text === 'function') {
        var fontSize = parseInt(svgTextElem.style("font-size").replace("px",""));
        var textLength = svgTextElem.text().length;

        return textLength * fontSize * 0.5;
    }
    return 0;
};

/* Numbers that are undefined, null or NaN, convert them to zeros.
*/
nv.utils.NaNtoZero = function(n) {
    if (typeof n !== 'number'
        || isNaN(n)
        || n === null
        || n === Infinity) return 0;

    return n;
};

/*
Snippet of code you can insert into each nv.models.* to give you the ability to
do things like:
chart.options({
  showXAxis: true,
  tooltips: true
});

To enable in the chart:
chart.options = nv.utils.optionsFunc.bind(chart);
*/
nv.utils.optionsFunc = function(args) {
    if (args) {
      d3.map(args).forEach((function(key,value) {
        if (typeof this[key] === "function") {
           this[key](value);
        }
      }).bind(this));
    }
    return this;
};
nv.models.axis = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var axis = d3.svg.axis()
    ;

  var margin = {top: 0, right: 0, bottom: 0, left: 0}
    , width = 75 //only used for tickLabel currently
    , height = 60 //only used for tickLabel currently
    , scale = d3.scale.linear()
    , axisLabelText = null
    , showMaxMin = true //TODO: showMaxMin should be disabled on all ordinal scaled axes
    , highlightZero = true
    , rotateLabels = 0
    , rotateYLabel = true
    , staggerLabels = false
    , isOrdinal = false
    , ticks = null
    , axisLabelDistance = 12 //The larger this number is, the closer the axis label is to the axis.
    ;

  axis
    .scale(scale)
    .orient('bottom')
    .tickFormat(function(d) { return d })
    ;

  //============================================================


  //============================================================
  // Private Variables
  //------------------------------------------------------------

  var scale0;

  //============================================================


  function chart(selection) {
    selection.each(function(data) {
      var container = d3.select(this);


      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      var wrap = container.selectAll('g.nv-wrap.nv-axis').data([data]);
      var wrapEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-axis');
      var gEnter = wrapEnter.append('g');
      var g = wrap.select('g')

      //------------------------------------------------------------


      if (ticks !== null)
        axis.ticks(ticks);
      else if (axis.orient() == 'top' || axis.orient() == 'bottom')
        axis.ticks(Math.abs(scale.range()[1] - scale.range()[0]) / 100);


      //TODO: consider calculating width/height based on whether or not label is added, for reference in charts using this component


      g.transition().call(axis);

      scale0 = scale0 || axis.scale();

      var fmt = axis.tickFormat();
      if (fmt == null) {
        fmt = scale0.tickFormat();
      }

      var axisLabel = g.selectAll('text.nv-axislabel')
          .data([axisLabelText || null]);
      axisLabel.exit().remove();
      switch (axis.orient()) {
        case 'top':
          axisLabel.enter().append('text').attr('class', 'nv-axislabel');
          var w = (scale.range().length==2) ? scale.range()[1] : (scale.range()[scale.range().length-1]+(scale.range()[1]-scale.range()[0]));
          axisLabel
              .attr('text-anchor', 'middle')
              .attr('y', 0)
              .attr('x', w/2);
          if (showMaxMin) {
            var axisMaxMin = wrap.selectAll('g.nv-axisMaxMin')
                           .data(scale.domain());
            axisMaxMin.enter().append('g').attr('class', 'nv-axisMaxMin').append('text');
            axisMaxMin.exit().remove();
            axisMaxMin
                .attr('transform', function(d,i) {
                  return 'translate(' + scale(d) + ',0)'
                })
              .select('text')
                .attr('dy', '-0.5em')
                .attr('y', -axis.tickPadding())
                .attr('text-anchor', 'middle')
                .text(function(d,i) {
                  var v = fmt(d);
                  return ('' + v).match('NaN') ? '' : v;
                });
            axisMaxMin.transition()
                .attr('transform', function(d,i) {
                  return 'translate(' + scale.range()[i] + ',0)'
                });
          }
          break;
        case 'bottom':
          var xLabelMargin = 36;
          var maxTextWidth = 30;
          var xTicks = g.selectAll('g').select("text");
          if (rotateLabels%360) {
            //Calculate the longest xTick width
            xTicks.each(function(d,i){
              var width = this.getBBox().width;
              if(width > maxTextWidth) maxTextWidth = width;
            });
            //Convert to radians before calculating sin. Add 30 to margin for healthy padding.
            var sin = Math.abs(Math.sin(rotateLabels*Math.PI/180));
            var xLabelMargin = (sin ? sin*maxTextWidth : maxTextWidth)+30;
            //Rotate all xTicks
            xTicks
              .attr('transform', function(d,i,j) { return 'rotate(' + rotateLabels + ' 0,0)' })
              .style('text-anchor', rotateLabels%360 > 0 ? 'start' : 'end');
          }
          axisLabel.enter().append('text').attr('class', 'nv-axislabel');
          var w = scale.range()[0];
          if(scale.range().length > 1){
              var w = (scale.range().length==2) ? scale.range()[1] : (scale.range()[scale.range().length-1]+(scale.range()[1]-scale.range()[0]));
          }else{
            
          }
          axisLabel
              .attr('text-anchor', 'middle')
              .attr('y', xLabelMargin)
              .attr('x', w/2);
          if (showMaxMin) {
          //if (showMaxMin && !isOrdinal) {
            var axisMaxMin = wrap.selectAll('g.nv-axisMaxMin')
                           //.data(scale.domain())
                           .data([scale.domain()[0], scale.domain()[scale.domain().length - 1]]);
            axisMaxMin.enter().append('g').attr('class', 'nv-axisMaxMin').append('text');
            axisMaxMin.exit().remove();
            axisMaxMin
                .attr('transform', function(d,i) {
                  return 'translate(' + (scale(d) + (isOrdinal ? scale.rangeBand() / 2 : 0)) + ',0)'
                })
              .select('text')
                .attr('dy', '.71em')
                .attr('y', axis.tickPadding())
                .attr('transform', function(d,i,j) { return 'rotate(' + rotateLabels + ' 0,0)' })
                .style('text-anchor', rotateLabels ? (rotateLabels%360 > 0 ? 'start' : 'end') : 'middle')
                .text(function(d,i) {
                  var v = fmt(d);
                  return ('' + v).match('NaN') ? '' : v;
                });
            axisMaxMin.transition()
                .attr('transform', function(d,i) {
                  //return 'translate(' + scale.range()[i] + ',0)'
                  //return 'translate(' + scale(d) + ',0)'
                  return 'translate(' + (scale(d) + (isOrdinal ? scale.rangeBand() / 2 : 0)) + ',0)'
                });
          }
          if (staggerLabels)
            xTicks
                .attr('transform', function(d,i) { return 'translate(0,' + (i % 2 == 0 ? '0' : '12') + ')' });

          break;
        case 'right':
          axisLabel.enter().append('text').attr('class', 'nv-axislabel');
          axisLabel
              .style('text-anchor', rotateYLabel ? 'middle' : 'begin')
              .attr('transform', rotateYLabel ? 'rotate(90)' : '')
              .attr('y', rotateYLabel ? (-Math.max(margin.right,width) + 12) : -10) //TODO: consider calculating this based on largest tick width... OR at least expose this on chart
              .attr('x', rotateYLabel ? (scale.range()[0] / 2) : axis.tickPadding());
          if (showMaxMin) {
            var axisMaxMin = wrap.selectAll('g.nv-axisMaxMin')
                           .data(scale.domain());
            axisMaxMin.enter().append('g').attr('class', 'nv-axisMaxMin').append('text')
                .style('opacity', 0);
            axisMaxMin.exit().remove();
            axisMaxMin
                .attr('transform', function(d,i) {
                  var dy = isNaN(scale(d)) ? 0 : scale(d);
                  return 'translate(0,' + dy + ')'
                })
              .select('text')
                .attr('dy', '.32em')
                .attr('y', 0)
                .attr('x', axis.tickPadding())
                .style('text-anchor', 'start')
                .text(function(d,i) {
                  var v = fmt(d);
                  return ('' + v).match('NaN') ? '' : v;
                });
            axisMaxMin.transition()
                .attr('transform', function(d,i) {
                  return 'translate(0,' + scale.range()[i] + ')'
                })
              .select('text')
                .style('opacity', 1);
          }
          break;
        case 'left':
          /*
          //For dynamically placing the label. Can be used with dynamically-sized chart axis margins
          var yTicks = g.selectAll('g').select("text");
          yTicks.each(function(d,i){
            var labelPadding = this.getBBox().width + axis.tickPadding() + 16;
            if(labelPadding > width) width = labelPadding;
          });
          */
          axisLabel.enter().append('text').attr('class', 'nv-axislabel');
          axisLabel
              .style('text-anchor', rotateYLabel ? 'middle' : 'end')
              .attr('transform', rotateYLabel ? 'rotate(-90)' : '')
              .attr('y', rotateYLabel ? (-Math.max(margin.left,width) + axisLabelDistance) : -10) //TODO: consider calculating this based on largest tick width... OR at least expose this on chart
              .attr('x', rotateYLabel ? (-scale.range()[0] / 2) : -axis.tickPadding());
          if (showMaxMin) {
            var axisMaxMin = wrap.selectAll('g.nv-axisMaxMin')
                           .data(scale.domain());
            axisMaxMin.enter().append('g').attr('class', 'nv-axisMaxMin').append('text')
                .style('opacity', 0);
            axisMaxMin.exit().remove();
            axisMaxMin
                .attr('transform', function(d,i) {
                  return 'translate(0,' + scale0(d) + ')'
                })
              .select('text')
                .attr('dy', '.32em')
                .attr('y', 0)
                .attr('x', -axis.tickPadding())
                .attr('text-anchor', 'end')
                .text(function(d,i) {
                  var v = fmt(d);
                  return ('' + v).match('NaN') ? '' : v;
                });
            axisMaxMin.transition()
                .attr('transform', function(d,i) {
                  return 'translate(0,' + scale.range()[i] + ')'
                })
              .select('text')
                .style('opacity', 1);
          }
          break;
      }
      axisLabel
          .text(function(d) { return d });


      if (showMaxMin && (axis.orient() === 'left' || axis.orient() === 'right')) {
        //check if max and min overlap other values, if so, hide the values that overlap
        g.selectAll('g') // the g's wrapping each tick
            .each(function(d,i) {
              d3.select(this).select('text').attr('opacity', 1);
              if (scale(d) < scale.range()[1] + 10 || scale(d) > scale.range()[0] - 10) { // 10 is assuming text height is 16... if d is 0, leave it!
                if (d > 1e-10 || d < -1e-10) // accounts for minor floating point errors... though could be problematic if the scale is EXTREMELY SMALL
                  d3.select(this).attr('opacity', 0);

                d3.select(this).select('text').attr('opacity', 0); // Don't remove the ZERO line!!
              }
            });

        //if Max and Min = 0 only show min, Issue #281
        if (scale.domain()[0] == scale.domain()[1] && scale.domain()[0] == 0)
          wrap.selectAll('g.nv-axisMaxMin')
            .style('opacity', function(d,i) { return !i ? 1 : 0 });

      }

      if (showMaxMin && (axis.orient() === 'top' || axis.orient() === 'bottom')) {
        var maxMinRange = [];
        wrap.selectAll('g.nv-axisMaxMin')
            .each(function(d,i) {
              try {
                  if (i) // i== 1, max position
                      maxMinRange.push(scale(d) - this.getBBox().width - 4)  //assuming the max and min labels are as wide as the next tick (with an extra 4 pixels just in case)
                  else // i==0, min position
                      maxMinRange.push(scale(d) + this.getBBox().width + 4)
              }catch (err) {
                  if (i) // i== 1, max position
                      maxMinRange.push(scale(d) - 4)  //assuming the max and min labels are as wide as the next tick (with an extra 4 pixels just in case)
                  else // i==0, min position
                      maxMinRange.push(scale(d) + 4)
              }
            });
        g.selectAll('g') // the g's wrapping each tick
            .each(function(d,i) {
              if (scale(d) < maxMinRange[0] || scale(d) > maxMinRange[1]) {
                if (d > 1e-10 || d < -1e-10) // accounts for minor floating point errors... though could be problematic if the scale is EXTREMELY SMALL
                  d3.select(this).remove();
                else
                  d3.select(this).select('text').remove(); // Don't remove the ZERO line!!
              }
            });
      }


      //highlight zero line ... Maybe should not be an option and should just be in CSS?
      if (highlightZero)
        g.selectAll('.tick')
          .filter(function(d) { return !parseFloat(Math.round(d.__data__*100000)/1000000) && (d.__data__ !== undefined) }) //this is because sometimes the 0 tick is a very small fraction, TODO: think of cleaner technique
            .classed('zero', true);

      //store old scales for use in transitions on update
      scale0 = scale.copy();

    });

    return chart;
  }


  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  // expose chart's sub-components
  chart.axis = axis;

  d3.rebind(chart, axis, 'orient', 'tickValues', 'tickSubdivide', 'tickSize', 'tickPadding', 'tickFormat');
  d3.rebind(chart, scale, 'domain', 'range', 'rangeBand', 'rangeBands'); //these are also accessible by chart.scale(), but added common ones directly for ease of use

  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.margin = function(_) {
    if(!arguments.length) return margin;
    margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
    margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
    return chart;
  }

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.ticks = function(_) {
    if (!arguments.length) return ticks;
    ticks = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.axisLabel = function(_) {
    if (!arguments.length) return axisLabelText;
    axisLabelText = _;
    return chart;
  }

  chart.showMaxMin = function(_) {
    if (!arguments.length) return showMaxMin;
    showMaxMin = _;
    return chart;
  }

  chart.highlightZero = function(_) {
    if (!arguments.length) return highlightZero;
    highlightZero = _;
    return chart;
  }

  chart.scale = function(_) {
    if (!arguments.length) return scale;
    scale = _;
    axis.scale(scale);
    isOrdinal = typeof scale.rangeBands === 'function';
    d3.rebind(chart, scale, 'domain', 'range', 'rangeBand', 'rangeBands');
    return chart;
  }

  chart.rotateYLabel = function(_) {
    if(!arguments.length) return rotateYLabel;
    rotateYLabel = _;
    return chart;
  }

  chart.rotateLabels = function(_) {
    if(!arguments.length) return rotateLabels;
    rotateLabels = _;
    return chart;
  }

  chart.staggerLabels = function(_) {
    if (!arguments.length) return staggerLabels;
    staggerLabels = _;
    return chart;
  };

  chart.axisLabelDistance = function(_) {
    if (!arguments.length) return axisLabelDistance;
    axisLabelDistance = _;
    return chart;
  };

  //============================================================


  return chart;
}
nv.models.legend = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var margin = {top: 5, right: 0, bottom: 5, left: 0}
    , width = 400
    , height = 20
    , getKey = function(d) { return d.key }
    , color = nv.utils.defaultColor()
    , align = true
    , rightAlign = true
    , updateState = true   //If true, legend will update data.disabled and trigger a 'stateChange' dispatch.
    , radioButtonMode = false   //If true, clicking legend items will cause it to behave like a radio button. (only one can be selected at a time)
    , dispatch = d3.dispatch('legendClick', 'legendDblclick', 'legendMouseover', 'legendMouseout', 'stateChange')
    ;

  //============================================================


  function chart(selection) {
    selection.each(function(data) {
      var availableWidth = width - margin.left - margin.right,
          container = d3.select(this);


      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      var wrap = container.selectAll('g.nv-legend').data([data]);
      var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-legend').append('g');
      var g = wrap.select('g');

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      //------------------------------------------------------------


      var series = g.selectAll('.nv-series')
          .data(function(d) { return d });
      var seriesEnter = series.enter().append('g').attr('class', 'nv-series')
          .on('mouseover', function(d,i) {
            dispatch.legendMouseover(d,i);  //TODO: Make consistent with other event objects
          })
          .on('mouseout', function(d,i) {
            dispatch.legendMouseout(d,i);
          })
          .on('click', function(d,i) {
            dispatch.legendClick(d,i);
            if (updateState) {
               if (radioButtonMode) {
                   //Radio button mode: set every series to disabled,
                   //  and enable the clicked series.
                   data.forEach(function(series) { series.disabled = true});
                   d.disabled = false;
               }
               else {
                   d.disabled = !d.disabled;
                   if (data.every(function(series) { return series.disabled})) {
                       //the default behavior of NVD3 legends is, if every single series
                       // is disabled, turn all series' back on.
                       data.forEach(function(series) { series.disabled = false});
                   }
               }
               dispatch.stateChange({
                  disabled: data.map(function(d) { return !!d.disabled })
               });
            }
          })
          .on('dblclick', function(d,i) {
            dispatch.legendDblclick(d,i);
            if (updateState) {
                //the default behavior of NVD3 legends, when double clicking one,
                // is to set all other series' to false, and make the double clicked series enabled.
                data.forEach(function(series) {
                   series.disabled = true;
                });
                d.disabled = false;
                dispatch.stateChange({
                    disabled: data.map(function(d) { return !!d.disabled })
                });
            }
          });
      seriesEnter.append('circle')
          .style('stroke-width', 2)
          .attr('class','nv-legend-symbol')
          .attr('r', 5);
      seriesEnter.append('text')
          .attr('text-anchor', 'start')
          .attr('class','nv-legend-text')
          .attr('dy', '.32em')
          .attr('dx', '8');
      series.classed('disabled', function(d) { return d.disabled });
      series.exit().remove();
      series.select('circle')
          .style('fill', function(d,i) { return d.color || color(d,i)})
          .style('stroke', function(d,i) { return d.color || color(d, i) });
      series.select('text').text(getKey);


      //TODO: implement fixed-width and max-width options (max-width is especially useful with the align option)

      // NEW ALIGNING CODE, TODO: clean up
      if (align) {

        var seriesWidths = [];
        series.each(function(d,i) {
              var legendText = d3.select(this).select('text');
              var nodeTextLength;
              try {
                nodeTextLength = legendText.getComputedTextLength();
                // If the legendText is display:none'd (nodeTextLength == 0), simulate an error so we approximate, instead
                if(nodeTextLength <= 0) throw Error();
              }
              catch(e) {
                nodeTextLength = nv.utils.calcApproxTextWidth(legendText);
              }

              seriesWidths.push(nodeTextLength + 28); // 28 is ~ the width of the circle plus some padding
            });

        var seriesPerRow = 0;
        var legendWidth = 0;
        var columnWidths = [];

        while ( legendWidth < availableWidth && seriesPerRow < seriesWidths.length) {
          columnWidths[seriesPerRow] = seriesWidths[seriesPerRow];
          legendWidth += seriesWidths[seriesPerRow++];
        }
        if (seriesPerRow === 0) seriesPerRow = 1; //minimum of one series per row


        while ( legendWidth > availableWidth && seriesPerRow > 1 ) {
          columnWidths = [];
          seriesPerRow--;

          for (var k = 0; k < seriesWidths.length; k++) {
            if (seriesWidths[k] > (columnWidths[k % seriesPerRow] || 0) )
              columnWidths[k % seriesPerRow] = seriesWidths[k];
          }

          legendWidth = columnWidths.reduce(function(prev, cur, index, array) {
                          return prev + cur;
                        });
        }

        var xPositions = [];
        for (var i = 0, curX = 0; i < seriesPerRow; i++) {
            xPositions[i] = curX;
            curX += columnWidths[i];
        }

        series
            .attr('transform', function(d, i) {
              return 'translate(' + xPositions[i % seriesPerRow] + ',' + (5 + Math.floor(i / seriesPerRow) * 20) + ')';
            });

        //position legend as far right as possible within the total width
        if (rightAlign) {
           g.attr('transform', 'translate(' + (width - margin.right - legendWidth) + ',' + margin.top + ')');
        }
        else {
           g.attr('transform', 'translate(0' + ',' + margin.top + ')');
        }

        height = margin.top + margin.bottom + (Math.ceil(seriesWidths.length / seriesPerRow) * 20);

      } else {

        var ypos = 5,
            newxpos = 5,
            maxwidth = 0,
            xpos;
        series
            .attr('transform', function(d, i) {
              var length = d3.select(this).select('text').node().getComputedTextLength() + 28;
              xpos = newxpos;

              if (width < margin.left + margin.right + xpos + length) {
                newxpos = xpos = 5;
                ypos += 20;
              }

              newxpos += length;
              if (newxpos > maxwidth) maxwidth = newxpos;

              return 'translate(' + xpos + ',' + ypos + ')';
            });

        //position legend as far right as possible within the total width
        g.attr('transform', 'translate(' + (width - margin.right - maxwidth) + ',' + margin.top + ')');

        height = margin.top + margin.bottom + ypos + 15;

      }

    });

    return chart;
  }


  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  chart.dispatch = dispatch;
  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
    margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.key = function(_) {
    if (!arguments.length) return getKey;
    getKey = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = nv.utils.getColor(_);
    return chart;
  };

  chart.align = function(_) {
    if (!arguments.length) return align;
    align = _;
    return chart;
  };

  chart.rightAlign = function(_) {
    if (!arguments.length) return rightAlign;
    rightAlign = _;
    return chart;
  };

  chart.updateState = function(_) {
    if (!arguments.length) return updateState;
    updateState = _;
    return chart;
  };

  chart.radioButtonMode = function(_) {
    if (!arguments.length) return radioButtonMode;
    radioButtonMode = _;
    return chart;
  };

  //============================================================


  return chart;
}

nv.models.pie = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var margin = {top: 0, right: 0, bottom: 0, left: 0}
    , width = 500
    , height = 500
    , getX = function(d) { return d.x }
    , getLabel = function(d) { return d.label }
    , getY = function(d) { return d.y }
    , getDescription = function(d) { return d.description }
    , id = Math.floor(Math.random() * 10000) //Create semi-unique ID in case user doesn't select one
    , color = nv.utils.defaultColor()
    , valueFormat = d3.format()
    , showLabels = true
    , pieLabelsOutside = false
    , donutLabelsOutside = false
    , labelType = "percent"
    , labelThreshold = .02 //if slice percentage is under this, don't show label
    , donut = false
    , labelSunbeamLayout = false
    , startAngle = false
    , endAngle = false
    , donutRatio = 0.5
    , dispatch = d3.dispatch('chartClick', 'elementClick', 'elementDblClick', 'elementMouseover', 'elementMouseout')
    ;

  //============================================================


  function chart(selection) {
    selection.each(function(data) {
      var availableWidth = width - margin.left - margin.right,
          availableHeight = height - margin.top - margin.bottom,
          radius = Math.min(availableWidth, availableHeight) / 2,
          arcRadius = radius-(radius / 5),
          container = d3.select(this);


      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      //var wrap = container.selectAll('.nv-wrap.nv-pie').data([data]);
      var wrap = container.selectAll('.nv-wrap.nv-pie').data(data);
      var wrapEnter = wrap.enter().append('g').attr('class','nvd3 nv-wrap nv-pie nv-chart-' + id);
      var gEnter = wrapEnter.append('g');
      var g = wrap.select('g');

      gEnter.append('g').attr('class', 'nv-pie');
      gEnter.append('g').attr('class', 'nv-pieLabels');

      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
      g.select('.nv-pie').attr('transform', 'translate(' + availableWidth / 2 + ',' + availableHeight / 2 + ')');
      g.select('.nv-pieLabels').attr('transform', 'translate(' + availableWidth / 2 + ',' + availableHeight / 2 + ')');

      //------------------------------------------------------------


      container
          .on('click', function(d,i) {
              dispatch.chartClick({
                  data: d,
                  index: i,
                  pos: d3.event,
                  id: id
              });
          });


      var arc = d3.svg.arc()
                  .outerRadius(arcRadius);

      if (startAngle) arc.startAngle(startAngle)
      if (endAngle) arc.endAngle(endAngle);
      if (donut) arc.innerRadius(radius * donutRatio);

      // Setup the Pie chart and choose the data element
      var pie = d3.layout.pie()
          .sort(null)
          .value(function(d) { return d.disabled ? 0 : getY(d) });

      var slices = wrap.select('.nv-pie').selectAll('.nv-slice')
          .data(pie);

      var pieLabels = wrap.select('.nv-pieLabels').selectAll('.nv-label')
          .data(pie);

      slices.exit().remove();
      pieLabels.exit().remove();

      var ae = slices.enter().append('g')
              .attr('class', 'nv-slice')
              .on('mouseover', function(d,i){
                d3.select(this).classed('hover', true);
                dispatch.elementMouseover({
                    label: getX(d.data),
                    value: valueFormat(getY(d.data)),
                    point: d.data,
                    pointIndex: i,
                    pos: [d3.event.pageX, d3.event.pageY],
                    id: id
                });
              })
              .on('mouseout', function(d,i){
                d3.select(this).classed('hover', false);
                dispatch.elementMouseout({
                    label: getX(d.data),
                    value: getY(d.data),
                    point: d.data,
                    index: i,
                    id: id
                });
              })
              .on('click', function(d,i) {
                dispatch.elementClick({
                    label: getX(d.data),
                    value: getY(d.data),
                    point: d.data,
                    index: i,
                    pos: d3.event,
                    id: id
                });
                d3.event.stopPropagation();
              })
              .on('dblclick', function(d,i) {
                dispatch.elementDblClick({
                    label: getX(d.data),
                    value: getY(d.data),
                    point: d.data,
                    index: i,
                    pos: d3.event,
                    id: id
                });
                d3.event.stopPropagation();
              });

        slices
            .attr('fill', function(d,i) {
                if(d.data && d.data.color){
                    return d.data.color;
                }else{
                    return color(d, i);
                }})
            .attr('stroke', function(d,i) { return color(d, i); });

        var paths = ae.append('path')
            .each(function(d) { this._current = d; });
            //.attr('d', arc);

        slices.select('path')
          .transition()
            .attr('d', arc)
            .attrTween('d', arcTween);

        if (showLabels) {
          // This does the normal label
          var labelsArc = d3.svg.arc().innerRadius(0);

          if (pieLabelsOutside){ labelsArc = arc; }

          if (donutLabelsOutside) { labelsArc = d3.svg.arc().outerRadius(arc.outerRadius()); }

          pieLabels.enter().append("g").classed("nv-label",true)
            .each(function(d,i) {
                var group = d3.select(this);

                group
                  .attr('transform', function(d) {
                       if (labelSunbeamLayout) {
                         d.outerRadius = arcRadius + 10; // Set Outer Coordinate
                         d.innerRadius = arcRadius + 15; // Set Inner Coordinate
                         var rotateAngle = (d.startAngle + d.endAngle) / 2 * (180 / Math.PI);
                         if ((d.startAngle+d.endAngle)/2 < Math.PI) {
                           rotateAngle -= 90;
                         } else {
                           rotateAngle += 90;
                         }
                         return 'translate(' + labelsArc.centroid(d) + ') rotate(' + rotateAngle + ')';
                       } else {
                         d.outerRadius = radius + 10; // Set Outer Coordinate
                         d.innerRadius = radius + 15; // Set Inner Coordinate
                         return 'translate(' + labelsArc.centroid(d) + ')'
                       }
                  });

                group.append('rect')
                    .style('stroke', '#fff')
                    .style('fill', '#fff')
                    .attr("rx", 3)
                    .attr("ry", 3);

                group.append('text')
                    .style('text-anchor', labelSunbeamLayout ? ((d.startAngle + d.endAngle) / 2 < Math.PI ? 'start' : 'end') : 'middle') //center the text on it's origin or begin/end if orthogonal aligned
                    .style('fill', '#000')

            });

          var labelLocationHash = {};
          var avgHeight = 14;
          var avgWidth = 140;
          var createHashKey = function(coordinates) {

              return Math.floor(coordinates[0]/avgWidth) * avgWidth + ',' + Math.floor(coordinates[1]/avgHeight) * avgHeight;
          };
          pieLabels.transition()
                .attr('transform', function(d) {
                  if (labelSunbeamLayout) {
                      d.outerRadius = arcRadius + 10; // Set Outer Coordinate
                      d.innerRadius = arcRadius + 15; // Set Inner Coordinate
                      var rotateAngle = (d.startAngle + d.endAngle) / 2 * (180 / Math.PI);
                      if ((d.startAngle+d.endAngle)/2 < Math.PI) {
                        rotateAngle -= 90;
                      } else {
                        rotateAngle += 90;
                      }
                      return 'translate(' + labelsArc.centroid(d) + ') rotate(' + rotateAngle + ')';
                    } else {
                      d.outerRadius = radius + 10; // Set Outer Coordinate
                      d.innerRadius = radius + 15; // Set Inner Coordinate

                      /*
                      Overlapping pie labels are not good. What this attempts to do is, prevent overlapping.
                      Each label location is hashed, and if a hash collision occurs, we assume an overlap.
                      Adjust the label's y-position to remove the overlap.
                      */
                      var center = labelsArc.centroid(d);
                      var hashKey = createHashKey(center);
                      if (labelLocationHash[hashKey]) {
                        center[1] -= avgHeight;
                      }
                      labelLocationHash[createHashKey(center)] = true;
                      return 'translate(' + center + ')'
                    }
                });
          pieLabels.select(".nv-label text")
                .style('text-anchor', labelSunbeamLayout ? ((d.startAngle + d.endAngle) / 2 < Math.PI ? 'start' : 'end') : 'middle') //center the text on it's origin or begin/end if orthogonal aligned
                .text(function(d, i) {
                  var percent = (d.endAngle - d.startAngle) / (2 * Math.PI);
                  var labelTypes = {
                    "key" : getLabel(d.data),
                    "value": valueFormat(getY(d.data)),
                    "percent": d3.format('.1%')(percent)
                  };
                  return (d.value && percent > labelThreshold) ? labelTypes[labelType] : '';
                });
        }
        else {
            pieLabels.select(".nv-label text")
                .style('text-anchor', labelSunbeamLayout ? ((d.startAngle + d.endAngle) / 2 < Math.PI ? 'start' : 'end') : 'middle') //center the text on it's origin or begin/end if orthogonal aligned
                .text(function(d, i) {
                  return '';
                });
        }


        // Computes the angle of an arc, converting from radians to degrees.
        function angle(d) {
          var a = (d.startAngle + d.endAngle) * 90 / Math.PI - 90;
          return a > 90 ? a - 180 : a;
        }

        function arcTween(a) {
          a.endAngle = isNaN(a.endAngle) ? 0 : a.endAngle;
          a.startAngle = isNaN(a.startAngle) ? 0 : a.startAngle;
          if (!donut) a.innerRadius = 0;
          var i = d3.interpolate(this._current, a);
          this._current = i(0);
          return function(t) {
            return arc(i(t));
          };
        }

        function tweenPie(b) {
          b.innerRadius = 0;
          var i = d3.interpolate({startAngle: 0, endAngle: 0}, b);
          return function(t) {
              return arc(i(t));
          };
        }

    });

    return chart;
  }


  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  chart.dispatch = dispatch;
  chart.options = nv.utils.optionsFunc.bind(chart);

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
    margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.values = function(_) {
    nv.log("pie.values() is no longer supported.");
    return chart;
  };

  chart.x = function(_) {
    if (!arguments.length) return getX;
    getX = _;
    return chart;
  };

  chart.y = function(_) {
    if (!arguments.length) return getY;
    getY = d3.functor(_);
    return chart;
  };

  chart.description = function(_) {
    if (!arguments.length) return getDescription;
    getDescription = _;
    return chart;
  };

  chart.showLabels = function(_) {
    if (!arguments.length) return showLabels;
    showLabels = _;
    return chart;
  };

  chart.showValues = function(_) {
    if (!arguments.length) return showLabels;
    showLabels = _;
    return chart;
  };

  chart.labelSunbeamLayout = function(_) {
    if (!arguments.length) return labelSunbeamLayout;
    labelSunbeamLayout = _;
    return chart;
  };

  chart.donutLabelsOutside = function(_) {
    if (!arguments.length) return donutLabelsOutside;
    donutLabelsOutside = _;
    return chart;
  };

  chart.pieLabelsOutside = function(_) {
    if (!arguments.length) return pieLabelsOutside;
    pieLabelsOutside = _;
    return chart;
  };

  chart.labelType = function(_) {
    if (!arguments.length) return labelType;
    labelType = _;
    labelType = labelType || "key";
    return chart;
  };

  chart.donut = function(_) {
    if (!arguments.length) return donut;
    donut = _;
    return chart;
  };

  chart.donutRatio = function(_) {
    if (!arguments.length) return donutRatio;
    donutRatio = _;
    return chart;
  };

  chart.startAngle = function(_) {
    if (!arguments.length) return startAngle;
    startAngle = _;
    return chart;
  };

  chart.endAngle = function(_) {
    if (!arguments.length) return endAngle;
    endAngle = _;
    return chart;
  };

  chart.id = function(_) {
    if (!arguments.length) return id;
    id = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = nv.utils.getColor(_);
    return chart;
  };

  chart.valueFormat = function(_) {
    if (!arguments.length) return valueFormat;
    valueFormat = _;
    return chart;
  };

  chart.labelThreshold = function(_) {
    if (!arguments.length) return labelThreshold;
    labelThreshold = _;
    return chart;
  };
  //============================================================


  return chart;
}

nv.models.pieChart = function() {
  "use strict";
  //============================================================
  // Public Variables with Default Settings
  //------------------------------------------------------------

  var pie = nv.models.pie()
    , legend = nv.models.legend()
    , controls = nv.models.legend();

  var margin = {top: 30, right: 20, bottom: 20, left: 20}
    , width = null
    , height = null
    , showControls = true
    , showValues = false
    , showLegend = true
    , color = nv.utils.defaultColor()
    , tooltips = true
    , tooltip = function(key, y, e, graph) {
        return '<h3>' + key + '</h3>' +
               '<p>' +  y + '</p>'
      }
    , state = {}
    , noData = "No Data Available."
    , dispatch = d3.dispatch('tooltipShow', 'tooltipHide', 'stateChange', 'changeState')
    , field_axis_y = null
    , controlWidth = function () {return showControls ? 80 : 0}
    ;

    controls.updateState(true);
  //============================================================


  //============================================================
  // Private Variables
  //------------------------------------------------------------

  var showTooltip = function(e, offsetElement) {
    var tooltipLabel = e.point.label;
    var left = e.pos[0] + ( (offsetElement && offsetElement.offsetLeft) || 0 ),
        top = e.pos[1] + ( (offsetElement && offsetElement.offsetTop) || 0),
        y = pie.valueFormat()(pie.y()(e.point)),
        content = tooltip(tooltipLabel, y, e, chart);

    nv.tooltip.show([left, top], content, e.value < 0 ? 'n' : 's', null, offsetElement);
  };

  //============================================================


  function chart(selection) {
    selection.each(function(data0) {
      var container = d3.select(this),
          that = this;

      var availableWidth = (width || parseInt(container.style('width')) || 960)
                             - margin.left - margin.right,
          availableHeight = (height || parseInt(container.style('height')) || 400)
                             - margin.top - margin.right

      chart.update = function() { container.transition().call(chart); };
      chart.container = this;

      var data = JSON.parse(JSON.stringify(data0));

        data.values.forEach(function (d) {
            if (field_axis_y) {
                d.value = d.values.filter(function (v) {
                    return v.field == field_axis_y;
                })[0].value;
            }
            return d;
        });
        data.values = data.values.filter(function (d) {
            return d.value != 0;
        })

      if (data.fields.length == 1) {
      // without group by
      // {
      //    fields: [
      //        {field, order, ordinal_values [{order, value, label, color}]}
      //    ]
      //    values : [
      //        {key : {key, value}, value}
      //        ...
      //    ]
      // }
      //=>
      // [
      //    {x, y, color, label},
      //    ....
      //]
          var datacolors = {},
              datalabels = {}
          data.fields[0].ordinal_values.map( function (f) {
              datacolors[f.value] = f.color //|| color();
              datalabels[f.value] = f.label || f.value;
          });
          data = data.values.map(function (d) {
              var key = d.keys[0].value;
              var x = key,
                  y = d.value,
                  fcolor = datacolors[key],
                  label = datalabels[key],
                  disabled = false;
              if (state && state.disabled && state.disabled[x]){
                  disabled = state.disabled[x];
              }
              return {x: x, y: y, color:fcolor, label:label, disabled: disabled}
          });
      }
      else if (data.fields.length > 1) {
      //  with group by
        //sort fields representation using order value
        data.fields.sort(function (a, b) {
            return a.order < b.order ? -1 : a.order > b.order ? 1 : 0
        });
        var fields = [],
            values = {};
        data.fields.map(function (f) {
            fields.push(f.field);
            values[f.field] = {label: f.label || f.field};
            f.ordinal_values.map(function (o) {
                values[f.field][o.value] = o.label || o.value;
            });
        });
        data = data.values.map(function (d) {
            var x = '',
                disabled = false,
                label = '';
            fields.forEach(function (f) {
                d.keys.map(function (k) {
                    if (k.key == f) {
                        x += k.value + '@' + f + ':';
                        label += values[f].label + ': ' + values[f][k.value] + ' / ';
                    }
                });
            });
            label = label.slice(0, label.length - 3);
              if (state && state.disabled && state.disabled[x]){
                  disabled = state.disabled[x];
              }
            return {x: x, y: d.value, label: label, disabled: disabled};
        });
      }

      //------------------------------------------------------------
      // Display No Data message if there's nothing to show.

      if (!data || !data.length) {
        var noDataText = container.selectAll('.nv-noData').data([noData]);

        noDataText.enter().append('text')
          .attr('class', 'nvd3 nv-noData')
          .attr('dy', '-.7em')
          .style('text-anchor', 'middle');

        noDataText
          .attr('x', margin.left + availableWidth / 2)
          .attr('y', margin.top + availableHeight / 2)
          .text(function(d) { return d });

        return chart;
      } else {
        container.selectAll('.nv-noData').remove();
      }

      //------------------------------------------------------------


      //------------------------------------------------------------
      // Setup containers and skeleton of chart

      var wrap = container.selectAll('g.nv-wrap.nv-pieChart').data([data]);
      var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-pieChart').append('g');
      var g = wrap.select('g');

      gEnter.append('g').attr('class', 'nv-pieWrap');
      gEnter.append('g').attr('class', 'nv-legendWrap');
      gEnter.append('g').attr('class', 'nv-controlsWrap');

      //------------------------------------------------------------

        //------------------------------------------------------------
        // Controls

        if (showControls) {
            var labelType = pie.labelType();
            var controlsData = [
            {
                    key : 'Value',
                    disabled : labelType != 'value'
                }, {
                    key : 'Percent',
                    disabled : labelType != 'percent'
                },
                {
                    key : 'Aff. Valeurs',
                    disabled : !pie.showLabels()
                },
            ];
            controls.width(controlWidth()).color(['#444', '#444', '#444']);
            g.select('.nv-controlsWrap')
            .datum(controlsData)
            .attr('transform', 'translate(0,' + (-margin.top) + ')')
            .call(controls);
        }

      //------------------------------------------------------------
      // Legend

      var legend_height = 0;

      if (showLegend) {
        legend
          .width( availableWidth - controlWidth())
          .key(function (d) {return d.label;});

        wrap.select('.nv-legendWrap')
            .datum(data)
            .call(legend)
            .attr('transform', 'translate(' + controlWidth() + ',' + (-margin.top) +')');

        legend_height = legend.height();

        availableHeight = (height || parseInt(container.style('height')) || 400)
                - margin.top - margin.right - legend_height;

      }

        //------------------------------------------------------------

      //------------------------------------------------------------


      wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');


      //------------------------------------------------------------
      // Main Chart Component(s)

      pie
        .width(availableWidth)
        .height(availableHeight);

      var pieWrap = g.select('.nv-pieWrap')
          .attr('transform', 'translate(0,' + (-margin.top + legend_height) + ')')
          .datum([data]);

      d3.transition(pieWrap).call(pie);

      //------------------------------------------------------------


      //============================================================
      // Event Handling/Dispatching (in chart's scope)
      //------------------------------------------------------------
      //
        controls.dispatch.on('legendClick', function (d, i) {
            controlsData = controlsData.map(function (s) {
                    s.disabled = true;
                    return s;
                });
            switch (d.key) {
            case 'Label':
                pie.labelType("key");
                break;
            case 'Value':
                pie.labelType("value");
                break;
            case 'Percent':
                pie.labelType("percent");
                break;
            case 'Aff. Valeurs':
                pie.showLabels(!pie.showLabels());
                break;
            }

            state.labelType = pie.labelType();
            dispatch.stateChange(state);
            chart.update();
        });


    legend.dispatch.on('legendClick', function (d) {
        var x = d.x;
        if (state && state.disabled && state.disabled[x]) {
            state.disabled[x] = !state.disabled[x];
        } else {
            if (!state.disabled) {
                state.disabled = {};
            }
            state.disabled[x] = true;
        }
    });

      legend.dispatch.on('stateChange', function(newState) {
        dispatch.stateChange(state);
        chart.update();
      });

      pie.dispatch.on('elementMouseout.tooltip', function(e) {
        dispatch.tooltipHide(e);
      });

      // Update chart from a state object passed to event handler
      dispatch.on('changeState', function(e) {

        if (typeof e.disabled !== 'undefined') {
          data.forEach(function(series) {
            series.disabled = e.disabled[i];
          });

          state.disabled = e.disabled;
        }

        chart.update();
      });

      //============================================================


    });

    return chart;
  }

  //============================================================
  // Event Handling/Dispatching (out of chart's scope)
  //------------------------------------------------------------

  pie.dispatch.on('elementMouseover.tooltip', function(e) {
    e.pos = [e.pos[0] +  margin.left, e.pos[1] + margin.top];
    dispatch.tooltipShow(e);
  });

  dispatch.on('tooltipShow', function(e) {
    if (tooltips) showTooltip(e);
  });

  dispatch.on('tooltipHide', function() {
    if (tooltips) nv.tooltip.cleanup();
  });

  //============================================================


  //============================================================
  // Expose Public Variables
  //------------------------------------------------------------

  // expose chart's sub-components
  chart.legend = legend;
  chart.dispatch = dispatch;
  chart.pie = pie;

  d3.rebind(chart, pie, 'valueFormat', 'values', 'x', 'y', 'description', 'id', 'showLabels', 'showValues', 'donutLabelsOutside', 'pieLabelsOutside', 'labelType', 'donut', 'donutRatio', 'labelThreshold');
  chart.options = nv.utils.optionsFunc.bind(chart);

    chart.field_axis_y = function(_){
        if (!arguments.length)
            return field_axis_y;
        field_axis_y = _;
        return chart;
    };

  chart.margin = function(_) {
    if (!arguments.length) return margin;
    margin.top    = typeof _.top    != 'undefined' ? _.top    : margin.top;
    margin.right  = typeof _.right  != 'undefined' ? _.right  : margin.right;
    margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
    margin.left   = typeof _.left   != 'undefined' ? _.left   : margin.left;
    return chart;
  };

  chart.width = function(_) {
    if (!arguments.length) return width;
    width = _;
    return chart;
  };

  chart.height = function(_) {
    if (!arguments.length) return height;
    height = _;
    return chart;
  };

  chart.color = function(_) {
    if (!arguments.length) return color;
    color = nv.utils.getColor(_);
    legend.color(color);
    pie.color(color);
    return chart;
  };

  chart.showLegend = function(_) {
    if (!arguments.length) return showLegend;
    showLegend = _;
    return chart;
  };

    chart.showControls = function (_) {
        if (!arguments.length)
            return showControls;
        showControls = _;
        return chart;
    };

  chart.tooltips = function(_) {
    if (!arguments.length) return tooltips;
    tooltips = _;
    return chart;
  };

  chart.tooltipContent = function(_) {
    if (!arguments.length) return tooltip;
    tooltip = _;
    return chart;
  };

  chart.state = function(_) {
    if (!arguments.length) return state;
    state = _;
    return chart;
  };

  chart.noData = function(_) {
    if (!arguments.length) return noData;
    noData = _;
    return chart;
  };

  //============================================================


  return chart;
}



nv.models.multiBarAndStack = function () {
    "use strict";
    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var margin = {
        top : 0,
        right : 0,
        bottom : 0,
        left : 0
    },
    width = 960,
    height = 500,
    x = d3.scale.ordinal(),
    y = d3.scale.linear(),
    y2 = d3.scale.linear(),
    field_axis_y = null,
    field_axis_y2 = null,
    id = Math.floor(Math.random() * 10000) //Create semi-unique ID in case user doesn't select one
,

    forceY = [0]// 0 is forced by default.. this makes sense for the majority of bar graphs... user can always do chart.forceY([]) to remove
,
    clipEdge = true,
    stacked = false,
    expanded = false,
    stackOffset = 'zero' // options include 'silhouette', 'wiggle', 'expand', 'zero', or a custom function
,
    color = nv.utils.defaultColor(),
    hideable = false,
    barColor = null // adding the ability to set the color for each rather than the whole group
,
    disabled = {}// used in conjunction with barColor to communicate from multiBarHorizontalChart what series are disabled
,
    delay = 1200,
    xDomain,
    yDomain,
    yDomain2,
    xRange,
    yRange,
    yRange2,
    valuesFormat = d3.format(),
    showValues = false,
    groupSpacing = 5,
    dispatch = d3.dispatch('chartClick', 'elementClick', 'elementDblClick', 'elementMouseover', 'elementMouseout');

    //============================================================
    //============================================================


    function chart(selection) {
        selection.each(function (data) {
            var availableWidth = width - margin.left - margin.right,
            availableHeight = height - margin.top - margin.bottom,
            container = d3.select(this);

            y.domain(yDomain || [0, d3.max(data.values, function (d) {
                        return stacked ? d.total : parseFloat(d.value);
                    })])
            .range(yRange || [availableHeight, 0]);
            /*PV 2014-04-18 comment it because I'm not really understand what's for ?!
            if (y.domain()[0] === y.domain()[1])
                y.domain()[0] ?
                y.domain([y.domain()[0] + y.domain()[0] * 0.01, y.domain()[1] - y.domain()[1] * 0.01])
                 : y.domain([-1, 1]);*/

            var y2min = d3.min(data.values, function (d) {
                        return stacked ? 0 : parseFloat(d.value2);
                    });
            var y2max = d3.max(data.values, function (d) {
                        return stacked ? d.total2 : parseFloat(d.value2);
                    });
            //add 5% up and down of the scale
            y2max = y2max + (y2max - y2min) / 20;
            y2min = y2min - (y2max - y2min) / 20;
            y2min = y2min < 0 ? 0 : y2min;
            
            y2.domain(yDomain2 || [y2min, y2max])
            .range(yRange2 || [availableHeight, 0]);


            var wrap = container.selectAll('g.nv-wrap.nv-multibar').data([[data.values]]);
            var wrapEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-multibar');
            var defsEnter = wrapEnter.append('defs');
            var gEnter = wrapEnter.append('g');
            var g = wrap.select('g');

            gEnter.append('g').attr('class', 'nv-groups');

            wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            //------------------------------------------------------------

            defsEnter.append('clipPath')
                .attr('id', 'nv-edge-clip-' + id)
                .append('rect');
            wrap.select('#nv-edge-clip-' + id + ' rect')
                .attr('width', availableWidth)
                .attr('height', availableHeight);

            g.attr('clip-path', clipEdge ? 'url(#nv-edge-clip-' + id + ')' : '');

            var groups = wrap.select('.nv-groups').selectAll('.nv-group')
                .data(function (d) {
                    return d
                }, function (d, i) {
                    return i
                });
            groups.enter().append('g')
                .style('stroke-opacity', 1e-6)
                .style('fill-opacity', 1e-6);
            groups.exit()
                .transition()
                .selectAll('rect.nv-bar')
                .delay(function (d, i) {
                    return i * delay / data[0].values.length;
                })
                .attr('y', function (d) {
                    return stacked ? y(d.y0) : y(0)
                })
                .attr('height', 0)
                .remove();
            groups
                .attr('class', function (d, i) {
                    return 'nv-group nv-series-' + i
                })
                .classed('hover', function (d) {
                    return d.hover
                })
                .style('fill', function (d, i) {
                    return color(d, i)
                })
                .style('stroke', function (d, i) {
                    return color(d, i)
                });
            groups
                .transition()
                .style('stroke-opacity', 1)
                .style('fill-opacity', .75);

            groups.selectAll('rect.nv-bar')
                .remove();
            groups.selectAll('text').remove();

            var bars = groups.selectAll('rect.nv-bar')
                .data(data.values);
            var barwidth;
            
            barwidth = (availableWidth) / 
                       (data.scales[0].lastBarPosition);
            groupSpacing = barwidth * 0.1;
            barwidth = (availableWidth - (groupSpacing * data.scales[0].spaceCountAfter)) / 
                       (data.scales[0].lastBarPosition);
            
            data.barwidth = barwidth;
            data.groupSpacing = groupSpacing;
            data.functX = function (d) {
                var currentScaleLevel = data.scales[0].values;
                var scaleValue;
                data.fields.forEach(function(e){
                    if(!e.stacked || !stacked){
                        var cur_set = d.keys.filter(function(el){
                            return el.key == e.field;
                        })[0];
                        var currentValue = currentScaleLevel.filter(function(el){
                            return cur_set.key === el.field && cur_set.value === el.value;
                        });
                        scaleValue = currentValue[0];
                        if (currentValue.length != 0){
                            currentScaleLevel = currentValue[0].values;
                        }else{
                            console.warn("field declaration missing: " + cur_set.key);
                        }
                    }
                });
                if(scaleValue)
                    return scaleValue.spaceCountBefore * this.groupSpacing + scaleValue.firstBarPosition * this.barwidth;
                return 0;
                
            };
            
            var get_field_label_from_ordinals_val_and_value =  function(ord_val, value){
                var f = ord_val.filter(function (g) {
                                    return g.value == value;
                                });
                return f[0].label;
            }
            // titles
            var construct_title_from_fields = function (fields, removeLastEntry) {
                var nb = data.fields.length;
                var t = data.fields.map(function (d, i) {
                        if(i != nb - 1 || !removeLastEntry){
                            var f = fields.filter(function (g) {
                                    return g.key == d.field;
                                });
                            return f[0] ? d.label + ': ' +
                                get_field_label_from_ordinals_val_and_value(d.ordinal_values, f[0].value ) +
                                '<br/>' : '';
                        } else {
                            return '';
                        }
                    });
                return t.reduce(function (a, b) {
                    return a.concat(b);
                });
            }
            var barsEnter = bars.enter().append('rect')
                .attr("class", "nv-bar")
                .attr("x", function (d) {
                    return data.functX(d);
                })
                .attr("width", data.barwidth)
                .attr("height", function (d, i) {
                     d.value = nv.utils.NaNtoZero(parseFloat(d.value));
                    return availableHeight - y(d.value);
                });
            if (stacked) {
                barsEnter.attr("y", function (d, i) {
                    d.value = nv.utils.NaNtoZero(parseFloat(d.value));
                    d.y0 = nv.utils.NaNtoZero(parseFloat(d.y0));
                    return y(d.value + d.y0);
                })
            } else {
                barsEnter.attr("y", function (d, i) {
                    return y(d.value);
                })
            }

            barsEnter.attr('class', function (d, i) {
                return 'nv-group nv-series-' + id
            })
            .classed('hover', function (d) {
                return d.hover
            })
            .style('fill', function (d, i) {
                return color(d.color ? d.color : color, i)
            })
            .style('stroke', function (d, i) {
                return color(d.color ? d.color : color, i)
            });
            bars
            .style('fill', function (d, i, j) {
                return color(d, j, i);
            })
            .style('stroke', function (d, i, j) {
                return color(d, j, i);
            })
            .on('mouseover', function (d, i) {
                d3.select(this).classed('hover', true);
                dispatch.elementMouseover({
                    value : d,
                    title2display: construct_title_from_fields(d.keys, false),
                    value2display: d.value,
                    point : d,
                    series : d,
                    pos : [0, 0],
                    pointIndex : i,
                    seriesIndex : d.series,
                    e : d3.event
                });
            })
            .on('mouseout', function (d, i) {
                d3.select(this).classed('hover', false);
                dispatch.elementMouseout();
            });

            bars
            .attr('class', function (d, i) {
                return 'nv-bar positive';
            })
            .transition();

            //display path
            //To show lines we have to order values by ordinals values
            groups.selectAll('path.nv-line')
                .remove();
            groups.selectAll('circle.nv-point').remove();
            
            if(!expanded && y2max){
                var linePaths = groups.selectAll('path.nv-line')
                                      .data([data.values]);
                var pointsEnter = groups.selectAll('circle.nv-point')
                    .data(data.values);
                var points = pointsEnter.enter().append('circle');
                /*
                // interpolate possible values : 
                linear - piecewise linear segments, as in a polyline.
                linear-closed - close the linear segments to form a polygon.
                step - alternate between horizontal and vertical segments, as in a step function.
                step-before - alternate between vertical and horizontal segments, as in a step function.
                step-after - alternate between horizontal and vertical segments, as in a step function.
                basis - a B-spline, with control point duplication on the ends.
                basis-open - an open B-spline; may not intersect the start or end.
                basis-closed - a closed B-spline, as in a loop.
                bundle - equivalent to basis, except the tension parameter is used to straighten the spline.
                cardinal - a Cardinal spline, with control point duplication on the ends.
                cardinal-open - an open Cardinal spline; may not intersect the start or end, but will
                                intersect other control points.
                cardinal-closed - a closed Cardinal spline, as in a loop.
                monotone - cubic interpolation that preserves monotonicity in y.
                */

                var linesEnter = linePaths.enter().append('path')
                    .attr("class",  'nv-line')
                    .style('fill-opacity', 0)
                    .attr('d',
                        d3.svg.line()
                            .interpolate('monotone')
                            //TODO: define what should we do! if you want to stop drawing line
                            //when a value2 is note define, uncomment this line:
                            //.defined(function(d, i){return parseInt(d.value2) > 0;})
                            .x(function(d,i) {
                                                return data.functX(d) + data.barwidth / 2; 
                                             })
                            .y(function(d,i) {
                                                 if (stacked) {
                                                    d.total2 = nv.utils.NaNtoZero(parseFloat(d.total2));
                                                    return y2(d.total2);
                                                 } else {
                                                    d.value2 = nv.utils.NaNtoZero(parseFloat(d.value2));
                                                    return y2(d.value2);
                                                 }
                                             })
                    );
                    

                points
                    .attr('cx', function(d,i) { return data.functX(d) + data.barwidth / 2; })
                    .attr('cy', function(d,i) { 
                                                 if (stacked) {
                                                    d.total2 = nv.utils.NaNtoZero(parseFloat(d.total2));
                                                    return y2(d.total2);
                                                 } else {
                                                    d.value2 = nv.utils.NaNtoZero(parseFloat(d.value2));
                                                    return y2(d.value2);
                                                 }
                                              })
                    .attr('r', '0.2em')
                    .style('stroke-width', 1)
                    .style('fill-opacity', 0)
                    .style('stroke-opacity', 1)
                    .attr('fill', '#454545')
                    .attr('class', 'nv-point')
                    .on('mouseover', function (d, i) {
                        var point = d3.select(this);
                        point.classed('hover', true);
                        point.attr('r', '0.5em');
                        dispatch.elementMouseover({
                            value : d,
                            title2display: construct_title_from_fields(d.keys, stacked),
                            value2display: stacked ? d.total2 : d.value2,
                            point : d,
                            series : d,
                            pos : [0, 0],
                            pointIndex : i,
                            seriesIndex : d.series,
                            e : d3.event
                        });
                    })
                    .on('mouseout', function (d, i) {
                        var point = d3.select(this);
                        point.classed('hover', false);
                        point.attr('r', '0.2em');
                        dispatch.elementMouseout();
                    });
            }//end of path

            if (barColor) {
                if (!disabled)
                    disabled = data.map(function () {
                            return true
                        });
                bars
                .style('fill', function (d, i, j) {
                    return d3.rgb(barColor(d, i)).darker(disabled.map(function (d, i) {
                            return i
                        }).filter(function (d, i) {
                            return !disabled[i]
                        })[j]).toString();
                })
                .style('stroke', function (d, i, j) {
                    return d3.rgb(barColor(d, i)).darker(disabled.map(function (d, i) {
                            return i
                        }).filter(function (d, i) {
                            return !disabled[i]
                        })[j]).toString();
                })
                ;
            }

            if (showValues) {
                var isValueDefine = data.values.some(function (d){
                                                            return d && d.value ? true : false;
                                                        });
                if(isValueDefine){
                    bars.enter().append('text')
                    .attr('class', 'valeurs')
                    .style('opacity', 1)
                    .style('text-anchor', 'middle')
                    .style('text-anchor', 'middle')
                    .style('fill', ' #000000')
                    .style('stroke', 'none')
                    .style('font-size', '14px')
                    .attr("x", function (d) {
                        return data.functX(d) + data.barwidth / 2;
                    })
                    .attr("y", function (d) {
                        return stacked ? y(d.value / 2 + d.y0) : y(d.value / 2);
                    })
                    .attr("dy", ".50em")
                    .text(function (d) {
                        return valuesFormat(d.value)
                    });
                }else if(pointsEnter && !expanded){
                    pointsEnter.enter().append('text')
                        .attr('class', 'valeurs')
                        .style('opacity', 1)
                        .style('text-anchor', 'left')
                        .style('fill', ' #000000')
                        .style('stroke', 'none')
                        .style('font-size', '12px')
                        .attr("x", function (d) {
                            return data.functX(d) + data.barwidth / 2 + 10;
                        })
                        .attr("y", function (d) {
                                    var y = 0;
                                     if (stacked) {
                                        d.total2 = nv.utils.NaNtoZero(parseFloat(d.total2));
                                        y = y2(d.total2);
                                     } else {
                                        d.value2 = nv.utils.NaNtoZero(parseFloat(d.value2));
                                        y = y2(d.value2);
                                     }
                                     return y;
                                  })
                        .attr("dy", ".40em")
                        .text(function (d) {
                            return valuesFormat(stacked ? d.total2 : d.value2)
                        });
                }

            }

        });
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    chart.dispatch = dispatch;

    chart.options = nv.utils.optionsFunc.bind(chart);

    chart.field_axis_y = function(_){
        if (!arguments.length)
            return field_axis_y;
        field_axis_y = _;
        return chart;
    };

    chart.field_axis_y2 = function(_){
        if (!arguments.length)
            return field_axis_y2;
        field_axis_y2 = _;
        return chart;
    };

    chart.valuesFormat = function (_) {
        if (!arguments.length)
            return valuesFormat;
        valuesFormat = _;
        return chart;
    };

    chart.margin = function (_) {
        if (!arguments.length)
            return margin;
        margin.top = typeof _.top != 'undefined' ? _.top : margin.top;
        margin.right = typeof _.right != 'undefined' ? _.right : margin.right;
        margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
        margin.left = typeof _.left != 'undefined' ? _.left : margin.left;
        return chart;
    };

    chart.width = function (_) {
        if (!arguments.length)
            return width;
        width = _;
        return chart;
    };

    chart.height = function (_) {
        if (!arguments.length)
            return height;
        height = _;
        return chart;
    };

    chart.xScale = function (_) {
        if (!arguments.length)
            return x;
        x = _;
        return chart;
    };

    chart.yScale = function (_) {
        if (!arguments.length)
            return y;
        y = _;
        return chart;
    };

    chart.yScale2 = function (_) {
        if (!arguments.length)
            return y2;
        y2 = _;
        return chart;
    };

    chart.xDomain = function (_) {
        if (!arguments.length)
            return xDomain;
        xDomain = _;
        return chart;
    };

    chart.yDomain = function (_) {
        if (!arguments.length)
            return yDomain;
        yDomain = _;
        return chart;
    };

    chart.xRange = function (_) {
        if (!arguments.length)
            return xRange;
        xRange = _;
        return chart;
    };

    chart.yRange = function (_) {
        if (!arguments.length)
            return yRange;
        yRange = _;
        return chart;
    };

    chart.forceY = function (_) {
        if (!arguments.length)
            return forceY;
        forceY = _;
        return chart;
    };

    chart.expanded = function (_) {
        if (!arguments.length)
            return expanded;
        expanded = _;
        return chart;
    };
    chart.stacked = function (_) {
        if (!arguments.length)
            return stacked;
        stacked = _;
        return chart;
    };

    chart.stackOffset = function (_) {
        if (!arguments.length)
            return stackOffset;
        stackOffset = _;
        return chart;
    };

    chart.clipEdge = function (_) {
        if (!arguments.length)
            return clipEdge;
        clipEdge = _;
        return chart;
    };

    chart.color = function (_) {
        if (!arguments.length)
            return color;
        color = nv.utils.getColor(_);
        return chart;
    };

    chart.barColor = function (_) {
        if (!arguments.length) {
            return barColor;
        }
        barColor = nv.utils.getColor(_);
        return chart;
    };

    chart.disabled = function (_) {
        if (!arguments.length)
            return disabled;
        disabled = _;
        return chart;
    };

    chart.showValues = function (_) {
        if (!arguments.length)
            return showValues;
        showValues = _;
        return chart;
    };

    chart.id = function (_) {
        if (!arguments.length)
            return id;
        id = _;
        return chart;
    };

    chart.hideable = function (_) {
        if (!arguments.length)
            return hideable;
        hideable = _;
        return chart;
    };

    chart.delay = function (_) {
        if (!arguments.length)
            return delay;
        delay = _;
        return chart;
    };

    chart.groupSpacing = function (_) {
        if (!arguments.length)
            return groupSpacing;
        groupSpacing = _;
        return chart;
    };

    //============================================================


    return chart;
}

nv.models.multiBarAndStackChart = function () {
    "use strict";
    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var multibar = nv.models.multiBarAndStack(),
    xAxis = nv.models.axis(),
    yAxis = nv.models.axis(),
    y2Axis = nv.models.axis(),
    legend = nv.models.legend(),
    controls = nv.models.legend();

    var margin = {
        top : 30,
        right : 90,
        bottom : 50,
        left : 60
    },
    width = null,
    height = null,
    color = nv.utils.defaultColor(),
    showControls = true,
    showControlHideNull = false,
    showValues = false,
    hideNullValues = true,
    showLegend = true,
    showXAxis = true,
    showYAxis = true,
    reduceXTicks = true, // if false a tick will show for every data point
    default_yAxis_tickFormat,
    staggerLabels = false,
    rotateLabels = 50,
    tooltips = true,
    field_axis_y = null,
    field_axis_y2 = null,
    tooltip = function (e, expanded, graph) {
        return '<h3>' + e.title2display + '</h3>' +
        '<p>' + yAxis.tickFormat()(e.value2display) + '</p>'
    },
    x //can be accessed via chart.xScale()
    ,
    y //can be accessed via chart.yScale()
    ,
    y2  //can be accessed via chart.yScale2()
    ,
    state = {},
    stacked = false,
    expanded = false,
    expandedFormat = d3.format('.1%'),
    noData = "No Data Available.",
    dispatch = d3.dispatch('tooltipShow', 'tooltipHide', 'stateChange'),
    controlWidth = function () {
        return showControls ? 260 : 0
    },
    transitionDuration = 250,
    groupSpacing = 0.05;

    var tabxAxises = [];
    yAxis
    .orient('left')
    .tickFormat(d3.format('1f'));
    y2Axis
    .orient('right')
    .tickFormat(d3.format('1f'));

    controls.updateState(true);
    //============================================================

    var firstDraw = true;
    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var showTooltip = function (e, offsetElement) {
        var content = tooltip(e, expanded, chart);
        nv.tooltip.show([e.e.pageX, e.e.pageY], content, e.value < 0 ? 'n' : 's', null, offsetElement);
    };

    //============================================================


    function chart(selection) {
        if(firstDraw){
            default_yAxis_tickFormat = yAxis.tickFormat();
            firstDraw = false;
        }
        selection.each(function (data0) {
            if (document.location.search.search("debug=") > 0)
                console.log(data0);
            stacked = multibar.stacked();
            showValues = multibar.showValues();
            expanded = multibar.expanded();
            var container = d3.select(this),
            that = this,
            data;
            data = JSON.parse(JSON.stringify(data0));

            if (expanded) {
                chart.yAxis.tickFormat(chart.expandedFormat());
            } else {
                chart.yAxis.tickFormat(default_yAxis_tickFormat);
            }
            chart.update = function () {
                container.datum(data0).transition().duration(transitionDuration).call(chart)
            };
            chart.container = this;

            var availableWidth = (width || parseInt(container.style('width')) || 960)
             - margin.left - margin.right,
            availableHeight = (height || parseInt(container.style('height')) || 400)
             - margin.top - margin.bottom;
             
            //sort fields representation using order value
            data.fields.sort(function (a, b) {
                return a.order < b.order ? -1 : a.order > b.order ? 1 : 0
            });

            //make sure stack value is last
            if (stacked){
                data.fields.sort(function (a, b) {
                    return !a.stacked && b.stacked ? -1 : a.stacked && !b.stacked ? 1 : 0
                })
            }
            
            //make sure the last field is stackeble
            data.fields[data.fields.length - 1].stacked = true;

            //manage filtered values and colors
            data.fields[data.fields.length - 1].ordinal_values.forEach(function (d, i) {
                    if (!d.color) {
                        d.color = d3.scale.category20().range()[i]; ;
                    }
                    d.disabled = false;
                    if (state && state.disabled && state.disabled[d.value]) {
                        d.disabled = state.disabled[d.value];
                    }
                    return d;
                });
            var filteredField = '';
            var filteredValues = []
            if (state && state.disabled) {
                filteredField = data.fields[data.fields.length - 1].field;
                filteredValues = data.fields[data.fields.length - 1].ordinal_values.filter(function (d) {
                        return d.disabled;
                    });
                filteredValues = filteredValues.map(function (d) {
                        return d.value;
                    });
                //remove disaled data
                data.values = data.values.filter(function (d) {
                        var value = d.keys.filter(function (d) {
                                return d.key == filteredField
                            })[0].value;
                        return filteredValues.indexOf(value) == -1;
                    });
            }
            //calculate domains for each levels
            var treeValues = [{values:[]}];
            var populateleaves = function(tree, values){
                tree.forEach(function(d){
                    if (d.values.length == 0){
                        d.values = JSON.parse(JSON.stringify(values));
                    }else{
                        populateleaves(d.values, values);
                    }
                });
            }
            var colors = [];
            var labels = {};
            var lastField = data.fields[data.fields.length - 1].field;
            var labelLength = 0;
            data.fields.map(function (d, i) {
                //make sure label is set on each field
                if (!d.label)
                    d.label = d.field;
                //sort ordianls values, if order is not define this will keep the 
                d.ordinal_values.sort(function (a, b) {
                    return a.order < b.order ? -1 : a.order > b.order ? 1 : 0;
                });
                //make sure order is defined, with a value (base 1 is requiered)
                var i = 1
                d.ordinal_values = d.ordinal_values.map(function(d){
                    d.order = i;
                    i++;
                    return d;
                });
                //get a distinct ordinals values and composed colors reference array and labels
                var ordinalsValue = d.ordinal_values
                    .map(function (e) {
                        if (!e.label) {
                            e.label = e.value
                        }
                        labels[e.value + '@' + d.field] = e.label;
                        if (e.color)
                            colors[e.value + '@' + d.field] = e.color;
                        return e.value;
                    });
                // we should filtered values if needs
                if (filteredField == d.field) {
                    ordinalsValue = ordinalsValue.filter(function (d) {
                            return filteredValues.indexOf(d) == -1;
                        });
                }
                if (!stacked || !d.stacked || field_axis_y == null) {
                    // create the possible values tree
                    var levelValues = d.ordinal_values.map(function(v){
                        if(v.label.length > labelLength){
                            labelLength = v.label.length;
                        } 
                        return {
                            field: d.field,
                            label: v.label,
                            value:v.value,
                            define: false,
                            values:[]
                        };
                    });
                    populateleaves(treeValues, levelValues);
                }
            });
            
            //estimate label max height to adpat bottom margin
            /* For situations where we want to approximate the width in pixels
                Forumla is : text.length * font-size * constant_factor
            */
            var sin = Math.abs(Math.sin(rotateLabels*Math.PI/180));
            margin.bottom  = (sin ? sin * (labelLength * 12 * 0.9) : (labelLength * 12 * 0.9)) +
                             15 * data.fields.length;

            //initialize value and value2, if it's come from oerp data
            // TODO: try to do it within an other map loop for optimization
            data.values.forEach(function (d) {
                if (field_axis_y) {
                    d.value = d.values.filter(function (v) {
                        return v.field == field_axis_y;
                    })[0].value;
                }
                if (field_axis_y2) {
                    d.value2 = d.values.filter(function (v) {
                        return v.field == field_axis_y2;
                    })[0].value;
                }
                return d;
            });

            if (stacked) {
                //add ordinal id on data
                var construct_id_from_fields = function (fields) {
                    var t = data.fields.map(function (d) {
                            var f = fields.filter(function (g) {
                                    return g.key == d.field && (!stacked || !d.stacked);
                                });
                            return f[0] ? f[0].value + '@' + f[0].key : '';
                        });
                    return t.reduce(function (a, b) {
                        return a.concat(b);
                    });
                }

                data.values.sort(function (a, b) {
                    var av = a.keys.filter(function (d) {
                            return d.key == lastField;
                        });
                    var bv = b.keys.filter(function (e) {
                            return e.key == lastField;
                        });
                    return av[0].value < bv[0].value ? -1 : av[0].value > bv[0].value ? 1 : 0
                });
                var agregate_data = [];
                var agregate_data2 = [];
                data.values.forEach(function (d) {
                        d.value = nv.utils.NaNtoZero(parseFloat(d.value));
                        d.value2 = nv.utils.NaNtoZero(parseFloat(d.value2));
                        d.id = construct_id_from_fields(d.keys);
                        d.y0 = agregate_data[d.id] ? agregate_data[d.id] : 0;
                        d.y20 = agregate_data2[d.id] ? agregate_data2[d.id] : 0;
                        agregate_data[d.id] ? agregate_data[d.id] += d.value : agregate_data[d.id] = d.value;
                        agregate_data2[d.id] ? agregate_data2[d.id] += d.value2 : agregate_data2[d.id] = d.value2;
                        return d;
                    });

                data.values.forEach(function (d) {
                        if (expanded) {
                            d.y0 = d.y0 / agregate_data[d.id];
                            if (agregate_data[d.id] && agregate_data[d.id] > 0) {
                                d.value = d.value / agregate_data[d.id];
                            } else {
                                d.value = 0;
                            }
                            d.total = 1;
                            
                            d.y20 = d.y20 / agregate_data2[d.id];
                            if (agregate_data2[d.id] && agregate_data2[d.id] > 0) {
                                d.value2 = d.value2 / agregate_data2[d.id];
                            } else {
                                d.value2 = 0;
                            }
                            d.total2 = 1;
                        } else {
                            d.total = agregate_data[d.id];
                            d.total2 = agregate_data2[d.id];
                        }
                        return d;
                    });

            }
            //apply colors 
            data.values.forEach(function (d) {
                    //test if data is used or not only when we want to hide null values
                    if(hideNullValues){
                        var currentTreeValues = treeValues[0].values;
                        data.fields.forEach(function(e){
                            if(!e.stacked || !stacked ){
                                var cur_set = d.keys.filter(function(el){
                                    return el.key == e.field;
                                })[0];
                                var currentValue = currentTreeValues.filter(function(el){
                                    return cur_set.key === el.field && cur_set.value === el.value;
                                });
                                if (currentValue.length != 0){
                                    currentValue[0].define = true;
                                    currentTreeValues = currentValue[0].values;
                                }else{
                                    console.warn("field declaration missing: " + cur_set)
                                }
                            }
                        });
                    }
                    var c = d.keys.filter(function (e) {
                            return e.key == lastField;
                        })[0];
                    if (c) {
                        d.color = colors[c.value + '@' + c.key];
                    }
                });
                
            //remove undefine values
            if(hideNullValues){
                var removeNullValues = function (ref){
                    var removeEls = ref.filter(function(e){
                        return !e.define;
                    });
                    removeEls.forEach(function(d){
                        ref.remove(ref.indexOf(d));
                    });
                    ref.forEach(function(d){
                        removeNullValues(d.values);
                    });
                }
                removeNullValues(treeValues[0].values);
            }
            //sort values to display lines
            //TODO: do not do that when there is no lines to display
            data.values.sort(function (a, b){
                //compare field position and ordinal values position for each levels
                var sort_result = 0;
                data.fields.forEach(function(d){
                    if (sort_result != 0) return;
                    var aOrder = d.ordinal_values.filter(function(f){
                                                        return f.value == a.keys.filter(function(e){
                                                            return e.key == d.field;})[0].value;
                                                        })[0].order;
                    var bOrder = d.ordinal_values.filter(
                                    function(f){
                                        return f.value == b.keys.filter(function(e){ return e.key == d.field;})[0].value;
                                    })[0].order;
                    sort_result =  aOrder < bOrder ? -1 : aOrder > bOrder ? 1 : 0;
                });
                return sort_result;
            });
            
            //construct scales
            //what's the good way to construct scale when we should remove null data ?
            //the first version used d3.scale.ordinal(), the problem was to remove null values.
            //so we create our own scale function where values of first level have an availableWidth
            //depending chids values.
            //our tree is sort in the displayed way, so we can just go throught the tree and count
            //position and group spacing position
            var barCount = 0;
            var spaceCount = 0;
            var prepareScale = function(val){
                spaceCount++;
                val.firstBarPosition = barCount;
                val.spaceCountBefore = spaceCount;
                if (val.values.length == 0) {
                    barCount++;
                }else{
                    val.values.forEach(function(el){
                        prepareScale(el);
                    });
                }
                val.spaceCountAfter = spaceCount;
                val.lastBarPosition = barCount;
                spaceCount++;
            };
            prepareScale(treeValues[0]);
            data.scales = treeValues;

            //------------------------------------------------------------
            // Display noData message if there's nothing to show.
            // TODO: Could be an other way to proceded to avoid an other loop on data
            var nonull = data.values.filter(function (d) {
                return nv.utils.NaNtoZero(parseFloat(d.value)) != 0 
                            || nv.utils.NaNtoZero(parseFloat(d.value2)) != 0;
            });
            if (!data || !data.values || !data.values.length || !nonull.length) {

                var noDataText = container.selectAll('.nv-noData').data([noData]);

                noDataText.enter().append('text')
                .attr('class', 'nvd3 nv-noData')
                .attr('dy', '-.7em')
                .style('text-anchor', 'middle');

                noDataText
                    .attr('x', margin.left + availableWidth / 2)
                    .attr('y', margin.top + availableHeight / 2)
                    .text(function (d) {
                                        return d
                                    });

                return chart;
            } else {
                container.selectAll('.nv-noData').remove();
            }

            //------------------------------------------------------------
            // Setup Scales

            x = multibar.xScale();
            y = multibar.yScale();
            y2 = multibar.yScale2();
            //------------------------------------------------------------

            //------------------------------------------------------------
            // Setup containers and skeleton of chart

            var wrap = container.selectAll('g.nv-wrap.nv-multiBarWithLegend').data([data.fields]);
            var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-multiBarWithLegend').append('g');
            var g = wrap.select('g');

            gEnter.append('g').attr('class', 'nv-x nv-axis');
            gEnter.append('g').attr('class', 'nv-y nv-axis');
            gEnter.append('g').attr('class', 'nv-y2 nv-axis');
            gEnter.append('g').attr('class', 'nv-barsWrap');
            gEnter.append('g').attr('class', 'nv-legendWrap');
            gEnter.append('g').attr('class', 'nv-controlsWrap');

            //------------------------------------------------------------
            // Legend

            if (showLegend) {
                legend.width(availableWidth - controlWidth());
                legend.key(function (d) {
                    return d.label;
                })

                g.select('.nv-legendWrap')
                .datum(data.fields[data.fields.length - 1].ordinal_values)
                .call(legend);

                if (margin.top != legend.height()) {
                    margin.top = legend.height();
                    availableHeight = (height || parseInt(container.style('height')) || 400)
                     - margin.top - margin.bottom;
                }

                g.select('.nv-legendWrap')
                .attr('transform', 'translate(' + controlWidth() + ',' + (-margin.top) + ')');
            }

            //------------------------------------------------------------


            //------------------------------------------------------------
            // Controls

            if (showControls) {
                var controlsData = []
                if (data.fields.length > 1) {
                    controlsData = [{
                            key : 'Groupe',
                            disabled : multibar.stacked() || multibar.expanded()
                        }, {
                            key : 'Empile',
                            disabled : !(multibar.stacked() && !multibar.expanded())
                        }, {
                            key : 'Proportion',
                            disabled : !multibar.expanded()
                        },
                    ];
                }
                controlsData = controlsData.concat([{
                                key : 'Aff. Valeurs',
                                disabled : !showValues
                            }]);
                            
                if(showControlHideNull){
                    controlsData = controlsData.concat([{
                                key : 'Supp. Valeurs nulles',
                                disabled : !hideNullValues
                            }]);
                }
                controls.width(controlWidth()).color(['#444', '#444', '#444']);

                g.select('.nv-controlsWrap')
                .datum(controlsData)
                .call(controls);

                if(margin.top < controls.height()){
                    margin.top = controls.height();
                    availableHeight = (height || parseInt(container.style('height')) || 400)
                     - margin.top - margin.bottom;
                }

                g.select('.nv-controlsWrap')
                .attr('transform', 'translate(0,' + (-margin.top) + ')')
            }

            //------------------------------------------------------------


            wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            g.select(".nv-y2.nv-axis")
                .attr("transform", "translate(" + availableWidth + ",0)");

            //------------------------------------------------------------
            // Main Chart Component(s)

            multibar
            .width(availableWidth)
            .height(availableHeight)
            .valuesFormat(yAxis.tickFormat());

            var barsWrap = g.select('.nv-barsWrap')
                .datum(data); //.filter(function(d) { return !d.disabled }))

            barsWrap.transition().call(multibar);

            //------------------------------------------------------------


            //------------------------------------------------------------
            // Setup Axes

            if (showXAxis) {
                //we are not using scale on x axis so we have to manage ourself x axis rendering
                //while using delete null values option
                
                //we don't want to display the last field on the xaxis because the information is 
                //display on the legend
                var level = data.fields.length + 1;
                if(field_axis_y)
                    level = data.fields.length;
                var flat_scales = [];
                var draw_x_axis = function(val){
                    if(level > 0){
                        if(val.label){
                            if (level)
                            var xx = (val.spaceCountBefore + 
                                       (val.spaceCountAfter - val.spaceCountBefore) / 2 
                                     ) * data.groupSpacing +
                                     (val.firstBarPosition + 
                                       (val.lastBarPosition - val.firstBarPosition) / 2 
                                     ) * data.barwidth;
                            flat_scales.push({
                                                field: val.field,
                                                label: val.label,
                                                level: level,
                                                x: xx,
                                                y: level * 15
                                             });
                        }
                    }
                    val.values.forEach(function (d){
                        level--;
                        draw_x_axis(d);
                        level++;
                    });
                };
                draw_x_axis(data.scales[0]);
                var xaxisdata = d3.nest()
                                .key(function(d) { return d.level;})
                                .entries(flat_scales);
                //cleanups
                g.select('.nv-x.nv-axis').selectAll('.nv-x.nv-axis.nv-level').remove();
                g.select('.nv-x.nv-axis').selectAll('.nv-x.nv-axis.nv-level')
                    .data(xaxisdata)
                    .enter()
                    .append('g')
                        .attr('class',function(d){ return 'nv-x nv-axis nv-level idx' + d.key;});
                
                var axises = g.selectAll('.nv-x.nv-axis.nv-level');
                axises.each(function (d){
                    var ticks = d3.select(this)
                        .selectAll('.nv-axislabel')
                        .data(d.values)
                        .enter();
                    ticks
                        .append('text')
                        .attr('class', 'nv-axislabel')
                        //.attr('dy', '.5em')
                        .attr('x', function(d){return d.x;})
                        .attr('y', function(d){return d.y;})
                        .attr('transform', function(d){
                            return 'rotate(' + rotateLabels + ' ' + d.x + ' ' + d.y + ')';
                        })
                        .style('text-anchor', rotateLabels != 0 ? 
                                    (rotateLabels%180 < rotateLabels ? 'end' : 'start') : 'middle')
                        .text(function(d) {return d.label;});
                    ticks
                        .append("line")
                        .attr("class", "nv-guideline")
                        .attr("x1", function(d) { return d.x;})
                        .attr("y1", 0)
                        .attr("x2", function(d) { return d.x;})
                        .attr("y2", function(d) { return d.y - 10});
                });
                 g.select('.nv-x.nv-axis')
                    .attr('transform', 'translate(' + 0 + ',' + availableHeight + ')')
            }

            if (showYAxis) {
                yAxis
                .scale(y)
                .ticks(availableHeight / 36)
                .tickSize(-availableWidth, 0);

                g.select('.nv-y.nv-axis').transition()
                .call(yAxis);
                
                if(!expanded){
                    y2Axis
                    .scale(y2)
                    .ticks(availableHeight / 36)
                    .tickSize(-5, 0);

                    g.select('.nv-y2.nv-axis').transition()
                    .call(y2Axis);
                }else{
                    g.select('.nv-y2.nv-axis').select('.nvd3.nv-wrap.nv-axis').remove();
                }
            }

            //------------------------------------------------------------


            //============================================================
            // Event Handling/Dispatching (in chart's scope)
            //------------------------------------------------------------

            legend.dispatch.on('legendClick', function (d, i) {
                if (state && state.disabled && state.disabled[d.value]) {
                    state.disabled[d.value] = !state.disabled[d.value];
                } else {
                    if (!state.disabled) {
                        state.disabled = {};
                    }
                    state.disabled[d.value] = true;
                }
            });

            legend.dispatch.on('stateChange', function (newState) {
                dispatch.stateChange(state);
                chart.update();
            });

            controls.dispatch.on('legendClick', function (d, i) {
                controlsData = controlsData.map(function (s) {
                        s.disabled = true;
                        return s;
                    });
                switch (d.key) {
                case 'Groupe':
                    multibar.stacked(false);
                    multibar.expanded(false);
                    break;
                case 'Empile':
                    multibar.stacked(true);
                    multibar.expanded(false);
                    break;
                case 'Proportion':
                    multibar.stacked(true);
                    multibar.expanded(true);
                    break;
                case 'Aff. Valeurs':
                    multibar.showValues(!multibar.showValues());
                    break;
                case 'Supp. Valeurs nulles':
                    hideNullValues = !hideNullValues;
                    break;
                }

                state.showValues = multibar.showValues();
                state.hideNullValues = hideNullValues;
                state.stacked = multibar.stacked();
                state.expanded = multibar.expanded();
                dispatch.stateChange(state);
                chart.update();
            });

            dispatch.on('tooltipShow', function (e) {
                if (tooltips)
                    showTooltip(e, that.parentNode)
            });
            //============================================================


        });

        return chart;
    }

    //============================================================
    // Event Handling/Dispatching (out of chart's scope)
    //------------------------------------------------------------

    multibar.dispatch.on('elementMouseover.tooltip', function (e) {
        e.pos = [e.pos[0] + margin.left, e.pos[1] + margin.top];
        dispatch.tooltipShow(e);
    });

    multibar.dispatch.on('elementMouseout.tooltip', function (e) {
        dispatch.tooltipHide(e);
    });
    dispatch.on('tooltipHide', function () {
        if (tooltips)
            nv.tooltip.cleanup();
    });

    //============================================================


    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    // expose chart's sub-components
    chart.dispatch = dispatch;
    chart.multibar = multibar;
    chart.legend = legend;
    chart.xAxis = tabxAxises[0];
    chart.yAxis = yAxis;
    chart.y2Axis = y2Axis;

    d3.rebind(chart, multibar, 'x', 'y', 'xDomain', 'yDomain', 'xRange', 'yRange', 'forceX', 'forceY', 'clipEdge',
        'id', 'stacked', 'expanded', 'showValues', 'stackOffset', 'delay', 'barColor', 'groupSpacing');

    chart.options = nv.utils.optionsFunc.bind(chart);

    chart.field_axis_y = function(_){
        if (!arguments.length)
            return field_axis_y;
        field_axis_y = _;
        return chart;
    };

    chart.field_axis_y2 = function(_){
        if (!arguments.length)
            return field_axis_y2;
        field_axis_y2 = _;
        return chart;
    };

    chart.hideNullValues = function(_){
        if (!arguments.length)
            return hideNullValues;
        hideNullValues = _;
        return chart;
    };
    chart.margin = function (_) {
        if (!arguments.length)
            return margin;
        margin.top = typeof _.top != 'undefined' ? _.top : margin.top;
        margin.right = typeof _.right != 'undefined' ? _.right : margin.right;
        margin.bottom = typeof _.bottom != 'undefined' ? _.bottom : margin.bottom;
        margin.left = typeof _.left != 'undefined' ? _.left : margin.left;
        return chart;
    };

    chart.width = function (_) {
        if (!arguments.length)
            return width;
        width = _;
        return chart;
    };

    chart.height = function (_) {
        if (!arguments.length)
            return height;
        height = _;
        return chart;
    };

    chart.color = function (_) {
        if (!arguments.length)
            return color;
        color = nv.utils.getColor(_);
        legend.color(color);
        return chart;
    };

    chart.showControls = function (_) {
        if (!arguments.length)
            return showControls;
        showControls = _;
        return chart;
    };

    chart.showControlHideNull = function (_) {
        if (!arguments.length)
            return showControlHideNull;
        showControlHideNull = _;
        return chart;
    };

    chart.showLegend = function (_) {
        if (!arguments.length)
            return showLegend;
        showLegend = _;
        return chart;
    };

    chart.showXAxis = function (_) {
        if (!arguments.length)
            return showXAxis;
        showXAxis = _;
        return chart;
    };

    chart.showYAxis = function (_) {
        if (!arguments.length)
            return showYAxis;
        showYAxis = _;
        return chart;
    };
    
    chart.reduceXTicks = function (_) {
        if (!arguments.length)
            return reduceXTicks;
        reduceXTicks = _;
        return chart;
    };

    chart.rotateLabels = function (_) {
        if (!arguments.length)
            return rotateLabels;
        rotateLabels = _;
        return chart;
    }

    chart.staggerLabels = function (_) {
        if (!arguments.length)
            return staggerLabels;
        staggerLabels = _;
        return chart;
    };

    chart.tooltip = function (_) {
        if (!arguments.length)
            return tooltip;
        tooltip = _;
        return chart;
    };

    chart.tooltips = function (_) {
        if (!arguments.length)
            return tooltips;
        tooltips = _;
        return chart;
    };

    chart.tooltipContent = function (_) {
        if (!arguments.length)
            return tooltip;
        tooltip = _;
        return chart;
    };

    chart.state = function (_) {
        if (!arguments.length)
            return state;
        state = _;
        return chart;
    };

    chart.noData = function (_) {
        if (!arguments.length)
            return noData;
        noData = _;
        return chart;
    };

    chart.transitionDuration = function (_) {
        if (!arguments.length)
            return transitionDuration;
        transitionDuration = _;
        return chart;
    };

    chart.expandedFormat = function (_) {
        if (!arguments.length)
            return expandedFormat;
        expandedFormat = _;
        return chart;
    };
    //============================================================


    return chart;
}
})();
