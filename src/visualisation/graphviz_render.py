"""
visualisation.graphviz_render

Render Graphviz DOT source to SVG.
"""

import graphviz


def dot_to_svg(dot_source: str) -> str:
    src = graphviz.Source(dot_source)
    return src.pipe(format="svg").decode("utf-8")
