/**
 * Graph visualization using D3.js.
 *
 * Renders a force-directed network graph from graph.json,
 * including:
 * - Nodes (hosts and routers)
 * - Edges between nodes
 * - Subnet group hulls
 *
 * Handles layout simulation, dragging, and dynamic updates.
 */

const svg = d3.select("#graph");
const width = window.innerWidth;
const height = window.innerHeight;
const container = svg.append("g");

const CONFIG = {
  linkDistance: 200,
  chargeStrength: -200,
  nodeRadius: 30,
  subnetPadding: 80,
  labelOffsetY: 50,
};

const zoom = d3.zoom()
  .scaleExtent([0.1, 5])
  .on("zoom", (event) => {
    container.attr("transform", event.transform);
  });

svg.call(zoom);

Promise.all([
  d3.json("http://localhost:8000/graph"),
]).then(([data]) => {

  if (!data.nodes || !data.edges) {
    console.error("Invalid graph data format", data);
    return;
  }

  data.nodes.forEach(node => {
    if (data.layout[node.id]) {
      const [x, y] = data.layout[node.id];
      node.x = x;
      node.y = y;
    }
  });

  console.debug("Graph data loaded", {
    nodes: data.nodes.length,
    edges: data.edges.length,
    subnets: data.subnets.length,
  });

  const nodeMap = new Map(data.nodes.map(d => [d.id, d]));

  // Define forces
  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.edges).id(d => d.id).distance(CONFIG.linkDistance))
    .force("charge", d3.forceManyBody().strength(CONFIG.chargeStrength))
    .force("center", d3.forceCenter(width / 2, height / 2))

  // Draw edges
  const edges = container.selectAll(".edge")
    .data(data.edges)
    .enter()
    .append("line")
    .attr("class", "edge")
    .attr("stroke", "#555")
    .attr("stroke-width", 2);

  // Draw subnet hulls
  const hullLineGenerator = d3.line().curve(d3.curveCatmullRomClosed.alpha(0.75));

  /**
   * Expand a convex hull outward by a given padding.
   *
   * @param {Array<[number, number]>} hull - Array of [x, y] points.
   * @param {number} padding - Distance to expand outward.
   * @returns {Array<[number, number]>} Padded hull points.
   */
  function padHull(hull, padding) {
    const cx = d3.mean(hull, d => d[0]);
    const cy = d3.mean(hull, d => d[1]);
    return hull.map(([x, y]) => {
      const dx = x - cx;
      const dy = y - cy;
      const len = Math.sqrt(dx * dx + dy * dy) || 1;
      return [x + (dx / len) * padding, y + (dy / len) * padding];
    });
  }

  const subnetPaths = container.selectAll(".subnet")
    .data(data.subnets)
    .enter()
    .append("path")
    .attr("class", "subnet")
    .attr("fill", "lightblue")
    .attr("stroke", "#888")
    .attr("stroke-width", 2)
    .attr("fill-opacity", 0.2);

  // Draw nodes
  const nodes = container.selectAll(".node")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("class", d => `node ${d.type}`)
    .attr("r", CONFIG.nodeRadius)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended)
    );

  // Draw labels
  const labels = container.selectAll(".label")
    .data(data.nodes)
    .enter()
    .append("text")
    .attr("text-anchor", "middle")
    .style("pointer-events", "none")
    .style("font-size", "15px")
    .text(d => d.type === "host" ? d.label : "router");

  // Update positions on each tick
  simulation.on("tick", () => {
    // Update nodes
    nodes.attr("cx", d => d.x)
      .attr("cy", d => d.y);

    // Update node labels
    labels.attr("x", d => d.x)
      .attr("y", d => d.y + CONFIG.labelOffsetY);

    // Update edges
    edges.attr("x1", d => nodeMap.get(d.source.id).x)
      .attr("y1", d => nodeMap.get(d.source.id).y)
      .attr("x2", d => nodeMap.get(d.target.id).x)
      .attr("y2", d => nodeMap.get(d.target.id).y);

    // Update subnet paths
    subnetPaths.attr("d", d => {
      const points = d.members
        .map(id => nodeMap.get(id))
        .filter(node => node)
        .map(node => [node.x, node.y]);
      if (points.length < 3) return null;

      const hull = d3.polygonHull(points);
      if (!hull) return null;

      const padded = padHull(hull, CONFIG.subnetPadding);
      return hullLineGenerator(padded);
    });
  });

  /**
   * Handle drag start event.
   */
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  /**
   * Handle dragging event.
   */
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  /**
   * Handle drag end event.
   */
  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
});
