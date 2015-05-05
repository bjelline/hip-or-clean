    var logger = { 
      'element': $('.logger') ,
      'log': function(s) {
        this.element.append($("<p>" + s + "</p>"));
      },
      'dir': function(s) {
        this.element.append($("<p>" + s + "</p>"));
      }
    };

    var margin = {top: 20, right: 15, bottom: 60, left: 60}
      , width = 960 - margin.left - margin.right
      , height = 500 - margin.top - margin.bottom;
    
    var x = d3.scale.linear()  
              // .domain([d3.min(data, function(d) { return d[0]; }), d3.max(data, function(d) { return d[0]; })])
              .domain([0,32])
              .range([ 0, width ]);
    
    var y = d3.scale.linear()
            // .domain([d3.min(data, function(d) { return d[1]; }), d3.max(data, function(d) { return d[1]; })])
            .domain([0,10])
            .range([ height, 0 ]);

    var chart = d3.select('#output')
      .append('svg:svg')
      .attr('width', width + margin.right + margin.left)
      .attr('height', height + margin.top + margin.bottom)
      .attr('class', 'chart')

    var main = chart.append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
      .attr('width', width)
      .attr('height', height)
      .attr('class', 'main')   
        
    // draw the x axis
    var xAxis = d3.svg.axis()
      .scale(x)
      .orient('bottom');

    main.append('g')
      .attr('transform', 'translate(0,' + height + ')')
      .attr('class', 'main axis date')
      .call(xAxis);

    // draw the y axis
    var yAxis = d3.svg.axis()
      .scale(y)
      .orient('left');

    var g = main.append("svg:g"); 
    g.attr('transform', 'translate(0,0)')
      .attr('class', 'main axis date')
      .call(yAxis);


    var data = [[ 7, 7.2, "BarKogi Korean Restaurant & Bar", "Food contact surface not properly washed"], 
                [11, 8.0, "Patsy's Italian Restaurant", "Food not protected from potential source of contamination"]]; // evil global!

    function load_and_display() {
      var q = $('#filter').val();
      console.log("searching for " + q);
      logger.log("searching for " + q);
      d3.json("/combined.json?filter=" + q, function(error, whole_json) {
        data = whole_json['data'];
        console.log("I got me some JSON! " + data.length  + " points")
        logger.log("I got me some JSON! " + data.length  + " points")
        var scatterplot = g.selectAll("scatter-dots").data(data, function(d) { return d; });
        scatterplot.data(data, function(d) { return d; });
        scatterplot.enter().append("svg:circle")
                  .attr("cx", function (d,i) { return x(d[0]); } )
                  .attr("cy", function (d) { return y(d[1]); } )
                  .attr("r", 8)
                  .append("svg:title")
                    .text(function(d) { return d[2] + ":" + d[0] + " / " + d[1] + "\n" + d[3]});
        scatterplot.exit().remove();
      });
    }

    $('#filter').on('change', load_and_display);
    load_and_display();
