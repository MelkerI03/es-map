import { highlightNode } from "./highlight.js";
import { resetGraph } from "./reset.js";

export function setupSelections({
  nodes,
  edges,
  subnetPaths,
  hostSidebar,
  updateHostSidebar,
}) {
  nodes.on("click", (event, d) => {
    event.stopPropagation();

    if (d.type !== "host") return;

    hostSidebar.open();
    updateHostSidebar(d);

    highlightNode({
      nodes,
      edges,
      subnetPaths,
      event,
    });
  });

  d3.select("svg").on("click", () => {
    resetGraph({ nodes, edges, subnetPaths });
  });
}
