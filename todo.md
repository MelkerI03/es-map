# Graphing

Since Graphviz does not support embedded svgs in final output, the nodes are blurry in the final image. This can be solved by exporting as a dotfile, running 'dot -Tplain <dotfile>' and extracting all coordinates. Now the image can be built without relying on graphics renderers.

Split hnx.draw into
    * draw_hyper_edges,
    * draw_hyper_edge_labels,
    * draw_hyper_labels, and
    * draw_hyper_nodes


This enables detailed control of edge distance, node size and so on.

Node size should scale with the amount of nodes (in the subnet?)
 most information can be passed as kwargs

Networkx placement generation must be more split. The subnets must not overlap
each node inside a subnet should also be further apart

root router should connect to cloud node if ip addresses that are outside the subnets are reached. The cloud should not have any information stored about it (IP addresses, hostnames and so on)



# Thesis

Start writing :-)


