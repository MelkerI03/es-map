import { CONFIG } from "./config.js";

export function createSimulation(nodes, edges, width, height) {
  return d3.forceSimulation(nodes)
    .force("link", d3.forceLink(edges).id(d => d.id).distance(CONFIG.linkDistance))
    .force("charge", d3.forceManyBody().strength(CONFIG.chargeStrength))
    .force("center", d3.forceCenter(width / 2, height / 2));
}
