import marimo

__generated_with = "0.23.5"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def import_marimo():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # Inspecting caches of closed graphs and of sources
    """)
    return


@app.cell(hide_code=True)
def introduction(mo):
    mo.md(r"""
    This notebook exhibits cached closed graphs and source graphs
    for the $F_4$ and $E_6$ computations.
    """)
    return


@app.cell(hide_code=True)
def configure_import_path():
    import sys

    SRC = "/home/brucewestbury/Research/trivalent-graphs/src"

    if SRC not in sys.path:
        sys.path.insert(0, SRC)
    return


@app.cell(hide_code=True)
def repository_path():
    from pathlib import Path

    REPO = Path("/home/brucewestbury/Research/trivalent-graphs")
    return (REPO,)


@app.cell(hide_code=True)
def imports_from_project():
    import re
    import shutil

    from cache_inspect.inspect import (
        cache_item,
        closed_cache_item_to_dot,
        load_json_cache,
        source_cache_item_to_dot,
    )
    from visualisation.graphviz_render import dot_to_svg

    return (
        cache_item,
        closed_cache_item_to_dot,
        dot_to_svg,
        load_json_cache,
        re,
        shutil,
        source_cache_item_to_dot,
    )


@app.cell(hide_code=True)
def helper_functions(re, shutil):
    def vertex_count_from_cache_name(filename):
        """Return the integer vertex count encoded in a cache filename."""
        match = re.search(r"(?:^|_)t(\d+)(?:\D|$)", filename)
        if match is None:
            raise ValueError(
                "Could not read the number of vertices from cache filename "
                f"{filename!r}; expected a substring such as 't14'."
            )
        return int(match.group(1))

    def cache_file_by_vertex_count(cache_dir):
        """Return a dictionary {t: path} for JSON cache files in cache_dir."""
        paths = sorted(cache_dir.glob("*.json"))
        result = {}
        for path in paths:
            t = vertex_count_from_cache_name(path.name)
            if t in result:
                raise ValueError(f"More than one cache file in {cache_dir} has t={t}.")
            result[t] = path
        return result

    def require_graphviz_dot():
        """Raise an exception if the Graphviz `dot` executable is unavailable."""
        if shutil.which("dot") is None:
            raise RuntimeError(
                "Graphviz is not installed, or its `dot` executable is not on PATH. "
                "Install Graphviz, then restart this notebook."
            )

    def selected_cache_item_markdown(
        mo, family_value, kind_value, cache_path, index, cache
    ):
        """Markdown summary of the current cache selection."""
        return mo.md(
            """
            ## Selected cache item

            - family: `{family}`
            - kind: `{kind}`
            - file: `{file}`
            - index: `{index}`
            - cache size: `{size}`
            """.format(
                family=family_value,
                kind=kind_value,
                file=cache_path.name,
                index=index,
                size=len(cache),
            )
        )

    return (
        cache_file_by_vertex_count,
        require_graphviz_dot,
        selected_cache_item_markdown,
    )


@app.cell(hide_code=True)
def selector_text(mo):
    mo.md(r"""
    ### Selectors

    There are two primary selectors. One chooses the family, $F_4$ or $E_6$.
    The other chooses the cache kind: closed graphs or sources.

    * For the $F_4$ family a **closed graph** is a connected trivalent graph
      of girth at least five.

    * For the $E_6$ family a **closed graph** is a connected bipartite
      trivalent graph of girth at least six.

    A **source** is almost a closed graph.

    * For the $F_4$ family a **source** is a connected graph with one vertex
      of degree four and all other vertices of degree three; there are no
      cycles of length less than four and any cycle of length four must contain
      the vertex of degree four.

    * For the $E_6$ family a **source** is a connected bipartite graph with one
      vertex of degree two, one vertex of degree four and all other vertices of
      degree three where the vertex of degree two and the vertex of degree four
      are connected by an edge. Furthermore there is no cycle of length two or
      four.
    """)
    return


@app.cell(hide_code=True)
def family_and_kind_selectors(mo):
    family = mo.ui.dropdown(
        options=["f4", "e6"],
        value="f4",
        label="Family",
    )

    kind = mo.ui.dropdown(
        options=["closed", "sources"],
        value="closed",
        label="Cache kind",
    )

    mo.hstack([family, kind])
    return family, kind


@app.cell(hide_code=True)
def selected_family_and_kind(family, kind):
    # Passing these ordinary values to later cells makes the dependencies
    # explicit: changing a selector changes these variables, so dependent cells
    # are re-run.
    family_value = family.value
    kind_value = kind.value
    return family_value, kind_value


@app.cell
def cache_selector_text(mo):
    mo.md(r"""
    The next selector chooses the number of trivalent vertices, $t$.
    Note that a trivalent graph has an even number of vertices.

    * For the $F_4$ family the possible values of $t$ are $t=10,12,14,16$.
      There is no trivalent graph of girth at least five with fewer than 10
      vertices. Moreover the only trivalent graph of girth at least five with
      10 vertices is the Petersen graph. We have not computed caches for
      $t>16$ as the case $t=16$ gives the polynomial relation.

    * For the $E_6$ family the possible values of $t$ are $t=14,16,18,20,22$.
      There is no bipartite trivalent graph of girth at least six with fewer
      than 14 vertices. We have not computed caches for $t>22$ as the case
      $t=22$ gives the polynomial relation.
    """)
    return


@app.cell(hide_code=True)
def available_cache_files(
    REPO,
    cache_file_by_vertex_count,
    family_value,
    kind_value,
):
    cache_dir = REPO / "projects" / family_value / "cache" / kind_value
    cache_files_by_t = cache_file_by_vertex_count(cache_dir)
    vertex_counts = sorted(cache_files_by_t)
    return cache_files_by_t, vertex_counts


@app.cell(hide_code=True)
def vertex_count_selector(mo, vertex_counts):
    if not vertex_counts:
        raise FileNotFoundError("No JSON cache files were found for this selection.")

    vertex_count = mo.ui.dropdown(
        options=vertex_counts,
        value=vertex_counts[0],
        label="Number of trivalent vertices",
    )
    return (vertex_count,)


@app.cell(hide_code=True)
def selected_vertex_count(vertex_count):
    t = vertex_count.value
    return (t,)


@app.cell(hide_code=True)
def selected_cache_path(cache_files_by_t, t):
    cache_path = cache_files_by_t[t]
    return (cache_path,)


@app.cell(hide_code=True)
def item_selector_text(mo):
    mo.md(r"""
    The following slider chooses the entry in the cache.
    """)
    return


@app.cell(hide_code=True)
def load_cache_and_make_index_selector(cache_path, load_json_cache, mo):
    cache = load_json_cache(cache_path)

    index = mo.ui.slider(
        start=0,
        stop=max(len(cache) - 1, 0),
        value=0,
        label="Item index: 0 to {}".format(len(cache) - 1),
    )

    index
    return cache, index


@app.cell(hide_code=True)
def selected_index(index):
    item_index = index.value
    return (item_index,)


@app.cell(hide_code=True)
def selected_cache_item_summary(
    cache,
    cache_path,
    family_value,
    item_index,
    kind_value,
    mo,
    selected_cache_item_markdown,
):
    selected_cache_item_markdown(
        mo=mo,
        family_value=family_value,
        kind_value=kind_value,
        cache_path=cache_path,
        index=item_index,
        cache=cache,
    )
    return


@app.cell(hide_code=True)
def dot_text(mo):
    mo.md(r"""
    This should be the DOT code of the graph.
    """)
    return


@app.cell(hide_code=True)
def make_dot(
    cache,
    cache_item,
    closed_cache_item_to_dot,
    item_index,
    kind_value,
    source_cache_item_to_dot,
):
    item = cache_item(cache, item_index)

    if kind_value == "closed":
        dot = closed_cache_item_to_dot(item)
    else:
        dot = source_cache_item_to_dot(item)

    dot
    return (dot,)


@app.cell(hide_code=True)
def render_svg(dot, dot_to_svg, require_graphviz_dot):
    require_graphviz_dot()
    svg = dot_to_svg(dot)
    return (svg,)


@app.cell(hide_code=True)
def graph_text(mo):
    mo.md(r"""
    This is the graph.
    """)
    return


@app.cell(hide_code=True)
def display_graph(mo, svg):
    mo.Html(svg)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
