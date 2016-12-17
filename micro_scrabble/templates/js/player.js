// create the svg
var svg = d3.select('#rack').append('svg')
  .attr({
    width: {{ num_letters }}*{{ square }},
    height: {{ square }}
  });

// calculate number of rows and columns
var squaresRow = Math.round({{ num_letters }});
var squaresColumn = Math.round(1);

var rectangles = svg.selectAll('g')
                            .data({{ letter_rack|tojson }})
                            .enter()
                            .append('g');

var rectangle_attrs = rectangles.append('rect')
                      .attr("width",{{ square }})
                      .attr("height",{{ square }})
                      .attr("x",function(d,i){return i*{{ square }};})
                      .attr("y",0)
                      .attr("fill","#E1BF9A")
                      .attr("stroke",'#fff');

var letter_rack = rectangles.append('text')
          .text(function(d){return d.letter;})
          .attr("x",function(d,i){return i*{{ square }}+{{ square }}/2;})
          .attr("y",0)
          .attr("font-family","helvetica")
          .attr("font-size","50px")
          .attr("font-weight","bold")
          .attr("dy", "1.25em")
          .attr("text-anchor","middle");

var letter_points = rectangles.append('text')
          .text(function(d){return d.points.toString();})
          .attr("x",function(d,i){return i*{{ square }}+0.8*{{ square }};})
          .attr("y",0.65*{{square}})
          .attr("font-family","helvetica")
          .attr("font-size","25px")
          .attr("font-weight","bold")
          .attr("dy", "1em")
          .attr("text-anchor","middle");
