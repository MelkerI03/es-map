export function resetGraph({ nodes, edges, subnetPaths, CONFIG }) {
  nodes.classed("selected", false).classed("dimmed", false);

  nodes.select("image")
    .transition()
    .duration(200)
    .attr("width", CONFIG.nodeIconSize)
    .attr("height", CONFIG.nodeIconSize)
    .attr("x", -CONFIG.nodeIconSize / 2)
    .attr("y", -CONFIG.nodeIconSize / 2);

  nodes.select("rect")
    .transition()
    .duration(200)
    .attr("width", CONFIG.nodeRectSize)
    .attr("height", CONFIG.nodeRectSize)
    .attr("x", -CONFIG.nodeRectSize / 2)
    .attr("y", -CONFIG.nodeRectSize / 2);

  nodes.select("text")
    .transition()
    .duration(200)
    .attr("y", CONFIG.labelOffsetY);

  edges.classed("dimmed", false);
  subnetPaths.classed("dimmed", false);
}
