export async function loadGraph() {
  const data = await d3.json("http://localhost:8000/graph");

  if (!data.nodes || !data.edges) {
    throw new Error("Invalid graph data format");
  }

  data.nodes.forEach((node) => {
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

  return data;
}
