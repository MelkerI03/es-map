import { loadGraph } from "./api.js";
import { initSidebar } from "./ui.js";
import { createSimulation } from "./simulation.js";
import { createDrag } from "./interactions.js";
import { renderGraph } from "./renderer.js";

const svg = d3.select("#graph");
const width = window.innerWidth;
const height = window.innerHeight;

const container = svg.append("g");

// Zoom
const zoom = d3.zoom()
  .scaleExtent([0.1, 5])
  .on("zoom", (event) => {
    container.attr("transform", event.transform);
  });

svg.call(zoom);

// UI
initSidebar();

// Main
loadGraph().then(data => {
  const simulation = createSimulation(data.nodes, data.edges, width, height);
  const drag = createDrag(simulation);

  renderGraph(container, data, simulation, drag);
});
