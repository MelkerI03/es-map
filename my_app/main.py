import graphviz


def main():
    dot = graphviz.Digraph(name="G", filename="out/cluster.gv")

    with dot.subgraph(
        name="cluster_0"
    ) as c:  # pyright: ignore[reportOptionalContextManager]
        c.attr(style="filled", color="lightgrey")
        c.node_attr.update(style="filled", color="white")
        c.edges([("a0", "a1"), ("a1", "a2"), ("a2", "a3")])
        c.attr(label="process #1")

    dot.edge("start", "a0")
    dot.edge("a3", "a0")
    dot.edge("a3", "end")

    dot.node("start", shape="Mdiamond")
    dot.node("end", shape="Msquare")
    print(dot)

    dot.view()


if __name__ == "__main__":
    main()
