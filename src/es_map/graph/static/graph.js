const svg = d3.select("#graph");
const width = window.innerWidth;
const height = window.innerHeight;

d3.json("graph.json").then(data => {

  const nodeMap = new Map(data.nodes.map(d => [d.id, d]));

  // --- Define forces
  const simulation = d3.forceSimulation(data.nodes)
    .force("link", d3.forceLink(data.edges).id(d => d.id).distance(200))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2))

  // --- Draw edges
  const edges = svg.selectAll(".edge")
    .data(data.edges)
    .enter()
    .append("line")
    .attr("class", "edge")
    .attr("stroke", "#555")
    .attr("stroke-width", 2);

  // --- Draw subnet hulls
  const line = d3.line().curve(d3.curveCatmullRomClosed.alpha(0.75));
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

  const subnetPaths = svg.selectAll(".subnet")
    .data(data.subnets)
    .enter()
    .append("path")
    .attr("class", "subnet")
    .attr("fill", "lightblue")
    .attr("stroke", "#888")
    .attr("stroke-width", 2)
    .attr("fill-opacity", 0.2);

  // --- Draw nodes
  const nodes = svg.selectAll(".node")
    .data(data.nodes)
    .enter()
    .append("circle")
    .attr("class", d => `node ${d.type}`)
    .attr("r", 30)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended)
    );

  // --- Draw labels
  const labels = svg.selectAll(".label")
    .data(data.nodes)
    .enter()
    .append("text")
    .attr("text-anchor", "middle")
    .style("pointer-events", "none")
    .style("font-size", "15px")
    .text(d => d.type === "host" ? d.label : "router");

  // --- Update positions on each tick
  simulation.on("tick", () => {
    // --- Update nodes and their labels
    nodes.attr("cx", d => d.x)
      .attr("cy", d => d.y);

    labels.attr("x", d => d.x)
      .attr("y", d => d.y + 50);

    // --- Update edges
    edges.attr("x1", d => nodeMap.get(d.source.id).x)
      .attr("y1", d => nodeMap.get(d.source.id).y)
      .attr("x2", d => nodeMap.get(d.target.id).x)
      .attr("y2", d => nodeMap.get(d.target.id).y);

    // --- Update subnet paths
    subnetPaths.attr("d", d => {
      const points = d.members
        .map(id => nodeMap.get(id))
        .filter(Boolean)
        .map(n => [n.x, n.y]);
      if (points.length < 3) return null;

      const hull = d3.polygonHull(points);
      if (!hull) return null;

      const padded = padHull(hull, 80); // subnet padding
      return line(padded);
    });
  });

  // --- Drag functions
  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
});
