
var getName = function getName(source){
    switch (source){
        case "google": return "Google trends";
        case "itj": return "Itjobswatch.co.uk";
        case "wiki": return "Wikipedia";
        case "sot": return "StackOverflow Questions";
        case "gitstars": return "GitHub Stars";
        case "sousers": return "StackOverflow Users";
        case "average": return "Average";
        default : return source;
    }
};
var getShortName = function getName(source){
    switch (source){
        case "google": return "Google";
        case "itj": return "Itjobs";
        case "wiki": return "Wikipedia";
        case "sot": return "SO Questions";
        case "sousers": return "SO Users";
        case "gitstars": return "Git Stars";
        case "average": return "Average";
        default : return source;
    }
};
var downloadURL = function downloadURL(url) {
    var hiddenIFrameID = 'hiddenDownloader',
        iframe = document.getElementById(hiddenIFrameID);
    if (iframe === null) {
        iframe = document.createElement('iframe');
        iframe.id = hiddenIFrameID;
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
    }
    iframe.src = url;
};
var downloadCsv = function downloadCsv(type){
    var args = Array.prototype.slice.call(arguments);
    var url = "/csv/" + args.join(',')+'.csv';
    downloadURL(url);
};
var margin = {top: 20, right: 80, bottom: 0, left: 50},
        width = 960 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom;

var parseDate = d3.time.format("%Y %m %d").parse;

var svg;
function update(error, data) {
    if (error){
        d3.select("#main").append("p").text("Error, sorry :(");
        d3.select("#main").append("p").text("May be data is not downloaded yet. You sure that something must be here? Please inform us using feedback form on the right.")
        return;
    }
    width =  parseInt(window.getComputedStyle(document.getElementById("plots")).width)


    var ids = get_ids();

    var main_data = {};
    for (var tid = 0; tid < ids.length; tid++) {
        main_data[data[ids[tid]].tech_name] = {data: data[ids[tid]].average.sort(function (b, a) {
            return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0;
            //return new Date(a.date) - new Date(b.date)
        }), style: "t" + tid};
    }
    var main_div = d3.select("#main");
    main_div.append("p").text("Average values ");

    var svg = main_div.append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
    main_div.append("div").attr("class", "link-box").append("a").text("Get normalized data")
            .attr("href", "javascript:downloadCsv('norm', 'average',"+ids+")");
    svg.width = width;
    svg.height = height;
    plot(svg, main_data);

    var srcs = ["itj", "sot", "sousers", "wiki", "gitstars", "google"];
    for (var sid = 0; sid < srcs.length; sid++){
        var source_data = {};
        for (var tid = 0; tid < ids.length; tid++) {
            if (data[ids[tid]][srcs[sid]]) {
                source_data[data[ids[tid]].tech_name] = {data: data[ids[tid]][srcs[sid]].sort(function (b, a) {
                    return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0;
                    //return new Date(a.date) - new Date(b.date)
                }), style: "t" + tid};
            }
        }
        if (Object.keys(source_data).length) {
            d3.select("#sources").append("p").text(getName(srcs[sid]));
            var svg_source = d3.select("#sources").append("svg")
                    .attr("width", (width + margin.left + margin.right) / 2)
                    .attr("height", (height + margin.top + margin.bottom) / 2)
                    .append("g")
                    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
            var link_box = d3.select("#sources").append("div").attr("class", "link-box");
            link_box.append("a").text("Get normalized data")
            .attr("href", "javascript:downloadCsv('norm', '"+srcs[sid]+"',"+ids+")");
            link_box.append("a").text("Get raw data")
            .attr("href", "javascript:downloadCsv('raw', '"+srcs[sid]+"',"+ids+")");
            svg_source.width = width / 2 - margin.right;
            svg_source.height = height / 2;
            plot(svg_source, source_data);
        }
    }
    for (var tid = 0; tid < ids.length; tid++) {
        var tech_data = {}
        var srcs = d3.keys(data[ids[tid]]).filter(function (name) {
            return name !== "tech_name"
        });
        for (var sid = 0; sid < srcs.length; sid++) {
            tech_data[srcs[sid]] = {data: data[ids[tid]][srcs[sid]].sort(function (b, a) {
                return (b.date > a.date) ? 1 : (b.date < a.date) ? -1 : 0;
                //return new Date(a.date) - new Date(b.date)
            }), style: srcs[sid]};
        }
        d3.select("#techs").append("p").text(data[ids[tid]].tech_name);
        var svg_tech = d3.select("#techs").append("svg")
                .attr("width", (width + margin.left + margin.right) / 2)
                .attr("height", (height + margin.top + margin.bottom) / 2)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        var link_box = d3.select("#techs").append("div").attr("class", "link-box");
        link_box.append("a").text("Get normalized data")
            .attr("href", "javascript:downloadCsv('norm', " + ids[tid]+")");
        link_box.append("a").text("Get raw data")
            .attr("href", "javascript:downloadCsv('raw', " + ids[tid]+")");
        svg_tech.width = width / 2 - margin.left;
        svg_tech.height = height / 2;
        plot(svg_tech, tech_data);
    }

}

function plot(svg, data, width, height) {
    var tech_names = d3.keys(data);
    var width = svg.width - 30;
    var height = svg.height - 40;

    var techs = tech_names.map(function (name) {
        return {
            name: name,
            style: data[name].style,
            data_points: data[name].data.map(function (d) {return {date: parseDate(d.date), value: +d.value};})
        };
    });
    var x = d3.time.scale()
            .range([0, width])
            .domain(d3.extent(techs[0].data_points, function (d) {return d.date;}));
    var y = d3.scale.linear()
            .range([height, 0])
            .domain([0, 1]);
                //d3.min(techs, function (c) {return d3.min(c.data_points, function (v) {return v.value;});}),
                //d3.max(techs, function (c) {return d3.max(c.data_points, function (v) {return v.value;});})
            //]);
    var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

    var yAxis = d3.svg.axis()
            .scale(y)
            .orient("left");

    var line = d3.svg.line()
            .interpolate("basis")
            .x(function (d) {
                return x(d.date);
            })
            .y(function (d) {
                return y(d.value);
            });

    svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);

    svg.append("g")
            .attr("class", "y axis")
            .call(yAxis);


    var source = svg.selectAll(".source")
            .data(techs)
            .enter().append("g")
            .attr("class", "source");
    source.append("path")
            .attr("class", function (d) {return "line " + d.style;})
            .attr("d", function (d) {return line(d.data_points);})
            .style("stroke-width", 2);

    var legend = [];
    for (var tech_name_id = 0; tech_name_id < tech_names.length; tech_name_id ++ ){
        legend[legend.length] = {name: tech_names[tech_name_id], x: width - 10, y: 15*tech_name_id + 15,
            style: data[tech_names[tech_name_id]].style};
    }

    var legend_img = svg.selectAll(".legend").data(legend).enter().append("g");
    legend_img.append("circle")
            .attr("cx", function (l) {return l.x;})
            .attr("cy", function (l) {return l.y;})
            .attr("r", 3)
            .attr("class", function (l) {return l.style;})
            .style("fill", "none").style("stroke-width", 5);
    legend_img.append("text")
            .attr("x", function(l){return l.x;})
            .attr("y", function(l){return l.y;})
            .attr("dx", "1.35em")
            .attr("dy", ".25em")
            .text(function (d) {
                return getShortName(d.name);
            });
}

function redraw(ids) {
    // delete all plots
    var plot_places = document.getElementsByClassName("plot-place");
    for (var ppi = 0; ppi < plot_places.length; ppi++) {
        for (var index = plot_places[ppi].childNodes.length - 1; index >= 0; index--) {
            plot_places[ppi].removeChild(plot_places[ppi].childNodes[index]);
        }
    }
    // Get normalized data and make new plots inside update
    d3.json("json/" + ids.join(), update);
}

function get_ids() {
    if (window.location.hash) {
        var ids = window.location.hash.slice(1).split(',').slice(0, 5);
        return ids;
    } else {
        return [];
    }
}

function set_ids(ids) {
    window.location.hash = ids.join();
    selectors_update();
}
function selectors_update() {
    var ids = get_ids();
    for (var tsid = 0; tsid < 5; tsid++) {
        selector = document.getElementById("ts_" + tsid);
        if (tsid < ids.length) {
            selector.className = "tech_selector";
            selector.value = ids[tsid];
        } else if (tsid == ids.length) {
            selector.className = "tech_selector";
            selector.value = "";
        } else {
            selector.className = "invis_selector";
        }

    }
    redraw(ids);
}
function page_load() {
    selectors_update();
}
function change_selection(sel_id) {
    var ids = get_ids();
    var selector = document.getElementById("ts_" + sel_id);
    var tech_id = selector.options[selector.selectedIndex].value;
    if (ids.length > sel_id) {
        ids[sel_id] = tech_id;
    } else {
        ids[ids.length] = tech_id;
    }
    set_ids(ids);

}

function remove_selector() {
    var ids = get_ids();
    if (ids.length > 1) {
        set_ids(ids.slice(0, -1));
    }
}

