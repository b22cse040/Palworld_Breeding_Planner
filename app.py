from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from io import BytesIO
import uuid

from src.pals import row_to_pal, ABILITY_COLS
from src.engine import get_breeding_combinations, sort_breeding_results

app = Flask(__name__)

# -------------------------
# Load pals
# -------------------------

df = pd.read_parquet("./data/pals.parquet")
PAL_BY_NAME = {
    row["name"]: row_to_pal(row)
    for _, row in df.iterrows()
}

GRAPH_STORE = {}

# -------------------------
# Routes
# -------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    results = None

    if request.method == "POST":
        selected = request.form["pals"].split(",")
        depth = int(request.form["depth"])
        # sort_by = request.form["sort_by"]

        pals = [PAL_BY_NAME[p] for p in selected]

        graphs = get_breeding_combinations(pals, depth)
        sorted_results = list(graphs.items())

        results = {}

        for pal, graph in sorted_results:
            d = graph.depth()
            gid = str(uuid.uuid4())
            GRAPH_STORE[gid] = graph
            results.setdefault(d, []).append((pal, graph, gid))

        results = dict(sorted(results.items(), key=lambda x: x[0]))
    return render_template(
        "index.html",
        pals=PAL_BY_NAME.keys(),
        abilities=ABILITY_COLS,
        results=results
    )


@app.route("/graph/<gid>")
def graph(gid):
    png = GRAPH_STORE[gid].visualize_png()
    return send_file(BytesIO(png), mimetype="image/png")


@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "").lower()

    prefix = [n for n in PAL_BY_NAME if n.lower().startswith(q)]
    contains = [n for n in PAL_BY_NAME if q in n.lower() and n not in prefix]

    return jsonify((prefix + contains)[:10])


if __name__ == "__main__":
    app.run(debug=True)
