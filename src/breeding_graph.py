import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO

from src.pals import Pal


class BreedingGraph:
    def __init__(self, root: Pal):
        self.root = root
        self.graph = nx.DiGraph()
        self.graph.add_node(root)

    def add_breeding(self, p1: Pal, p2: Pal, child: Pal):
        label = f"{p1.name} x {p2.name}"
        self.graph.add_edge(p1, child, label=label)
        self.graph.add_edge(p2, child, label=label)

    def merge(self, other: "BreedingGraph"):
        self.graph = nx.compose(self.graph, other.graph)

    def depth(self) -> int:
        if not self.graph.edges:
            return 0

        lengths = []
        for node in self.graph.nodes:
            try:
                lengths.append(
                    nx.shortest_path_length(self.graph, node, self.root)
                )
            except nx.NetworkXNoPath:
                pass

        return max(lengths, default=0)

    def unique_pal_count(self) -> int:
        return len([n for n in self.graph.nodes if isinstance(n, Pal)])

    def contains(self, pal: Pal) -> bool:
        return pal in self.graph.nodes

    # Visualize on flask as a png
    def visualize_png(self) -> bytes:
        pos = nx.spring_layout(self.graph, seed=42)

        fig, ax = plt.subplots(figsize=(9, 6))

        nx.draw(
            self.graph,
            pos,
            ax=ax,
            with_labels=True,
            labels={n: n.name for n in self.graph.nodes},
            node_size=2400,
            node_color="#EAF2FF",
            edge_color="#333",
            font_size=9,
            arrows=True,
        )

        edge_labels = {
            (u, v): d.get("label", "")
            for u, v, d in self.graph.edges(data=True)
        }

        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels=edge_labels,
            font_size=8,
            ax=ax
        )

        ax.set_title(f"Breeding Graph: {self.root.name}")
        ax.axis("off")

        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)

        buf.seek(0)
        return buf.getvalue()
