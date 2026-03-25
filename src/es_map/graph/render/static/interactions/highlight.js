import { resetGraph } from "./reset.js";
import { CONFIG } from "../config.js";

export function highlightNode({ nodes, edges, subnetPaths, event }) {
  resetGraph({ nodes, edges, subnetPaths });

  nodes.classed("selected", false).classed("dimmed", true);
  edges.classed("dimmed", true);
  subnetPaths.classed("dimmed", true);

  const selectedNode = d3.select(event.currentTarget);

  selectedNode.classed("selected", true).classed("dimmed", false);

  selectedNode
    .select("image")
    .transition()
    .duration(200)
    .attr("width", CONFIG.nodeIconSize * CONFIG.selectedScale)
    .attr("height", CONFIG.nodeIconSize * CONFIG.selectedScale)
    .attr("x", (-CONFIG.nodeIconSize / 2) * CONFIG.selectedScale)
    .attr("y", (-CONFIG.nodeIconSize / 2) * CONFIG.selectedScale);

  selectedNode
    .select("rect")
    .transition()
    .duration(200)
    .attr("width", CONFIG.nodeRectSize * CONFIG.selectedScale)
    .attr("height", CONFIG.nodeRectSize * CONFIG.selectedScale)
    .attr("x", (-CONFIG.nodeRectSize / 2) * CONFIG.selectedScale)
    .attr("y", (-CONFIG.nodeRectSize / 2) * CONFIG.selectedScale);

  selectedNode
    .select("text")
    .transition()
    .duration(200)
    .attr("y", (CONFIG.labelOffsetY * (CONFIG.selectedScale + 1)) / 2);
}
