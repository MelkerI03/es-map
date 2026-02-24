# Graphing

Since Graphviz does not support embedded svgs in final output, the nodes are blurry in the final image. This can be solved by exporting as a dotfile, running 'dot -Tplain <dotfile>' and extracting all coordinates. Now the image can be built without relying on graphics renderers.
