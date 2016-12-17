// create the svg
var svg = d3.select('#grid').append('svg')
  .attr({
    width: {{ width }},
    height: {{ height }}
  });

// calculate number of rows and columns
var squaresRow = Math.round({{ width }}/ {{ square }});
var squaresColumn = Math.round({{ height }} / {{ square }});

var rectangles = svg.selectAll('g')
                            .data({{ board_matrix|tojson }})
                            .enter()
                            .append('g');

var rectangle_attrs = rectangles.append('rect')
                      .attr("width",{{ square }})
                      .attr("height",{{ square }})
                      .attr("x",function(d){return d.x*{{ square }};})
                      .attr("y",function(d){return d.y*{{ square }};})
                      .attr("fill",function(d){return d.color;})
                      .attr("stroke",'#fff');

var letter_labels = rectangles.append('text')
          .text(function(d){
            if(d.letter==null){
              return d.label;}
            else{
              return d.letter;}
            })
          .attr("x",function(d){return d.x*{{ square }}+{{ square }}/2;})
          .attr("y",function(d){return d.y*{{ square }};})
          .attr("font-family","helvetica")
          .attr("font-size",function(d){if(d.letter){return "25px";}else{return "15px";}})
          .attr("font-weight",function(d){if(d.letter){return "bold";}else{return "normal";}})
          .attr("dy", function(d){if(d.letter){return "1.4em";}else{return "2em";}})
          .attr("text-anchor","middle");

var point_labels = rectangles.append('text')
          .text(function(d){
            if(d.points>0){
              return d.points.toString();}
            })
          .attr("x",function(d){return d.x*{{ square }}+0.8*{{ square }};})
          .attr("y",function(d){return d.y*{{ square }}+{{ square }}*0.65;})
          .attr("font-family","helvetica")
          .attr("font-size","12.5px")
          .attr("font-weight","bold")
          .attr("dy","1em")
          .attr("text-anchor","middle");

//d3plus.textwrap().container(board_labels).resize(true).draw()
