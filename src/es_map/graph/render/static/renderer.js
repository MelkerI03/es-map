import { CONFIG } from "./config.js";
import { padHull } from "./utils.js";
import { updateHostSidebar } from "./ui.js";

export function renderGraph(container, data, simulation, drag, hostSidebar) {
  const nodeMap = new Map(data.nodes.map(d => [d.id, d]));

  const edges = container.selectAll(".edge")
    .data(data.edges)
    .enter()
    .append("line")
    .attr("class", "edge")
    .attr("stroke", "#555")
    .attr("stroke-width", 2);

  const subnetPaths = container.selectAll(".subnet")
    .data(data.subnets)
    .enter()
    .append("path")
    .attr("class", "subnet")
    .attr("fill", "lightblue")
    .attr("stroke", "#888")
    .attr("stroke-width", 2)
    .attr("fill-opacity", 0.2);

  const nodes = container.selectAll(".node")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("class", d => `node ${d.type}`)
    .attr("r", CONFIG.nodeRadius)
    .call(drag);

  const labels = container.selectAll(".label")
    .data(data.nodes)
    .enter()
    .append("text")
    .attr("text-anchor", "middle")
    .style("pointer-events", "none")
    .style("font-size", "15px")
    .text(d => d.type === "host" ? d.label : "router");

  const line = d3.line().curve(d3.curveCatmullRomClosed.alpha(0.75));

  simulation.on("tick", () => {
    nodes.attr("cx", d => d.x)
      .attr("cy", d => d.y);

    labels.attr("x", d => d.x)
      .attr("y", d => d.y + CONFIG.labelOffsetY);

    edges.attr("x1", d => nodeMap.get(d.source.id).x)
      .attr("y1", d => nodeMap.get(d.source.id).y)
      .attr("x2", d => nodeMap.get(d.target.id).x)
      .attr("y2", d => nodeMap.get(d.target.id).y);

    subnetPaths.attr("d", d => {
      const points = d.members
        .map(id => nodeMap.get(id))
        .filter(Boolean)
        .map(n => [n.x, n.y]);

      if (points.length < 3) return null;

      const hull = d3.polygonHull(points);
      if (!hull) return null;

      return line(padHull(hull, CONFIG.subnetPadding));
    });
  });

  nodes.on("click", (event, d) => {
    event.stopPropagation();

    if (d.type === "host") {
      hostSidebar.open();
      updateHostSidebar(d);
    }
  });
}
