from flask import Flask, jsonify, request, render_template, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io, base64
import matplotlib.ticker as mtick

# -------------------------------------------------------
# GLOBAL STYLE (white bg, black edges)
# -------------------------------------------------------
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "text.color": "black",
    "patch.edgecolor": "black"
})

app = Flask(__name__)
df_global = None


# -------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


# -------------------------------------------------------
# HOME / UPLOAD
# -------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    global df_global

    if request.method == "GET":
        uploaded_flag = request.args.get("uploaded")
        return render_template("home.html", uploaded=uploaded_flag)

    # POST → upload CSV
    file = request.files.get("file")
    if not file:
        return render_template("home.html", error="Please upload a CSV file.")

    try:
        df_global = pd.read_csv(file)

        # Clean column names
        df_global.columns = (
            df_global.columns
            .str.strip()
            .str.replace(" ", "_")
            .str.replace(r"[^\w]", "", regex=True)
        )

        # Smart numeric conversion
        for col in df_global.columns:
            cleaned = df_global[col].astype(str).str.replace(",", "")
            numeric_ratio = cleaned.str.match(r"^-?\d+(\.\d+)?$").mean()
            if numeric_ratio > 0.8:
                df_global[col] = pd.to_numeric(cleaned, errors="coerce")

        # Parse YYYYMM → datetime
        for col in df_global.columns:
            s = df_global[col].astype(str)
            if s.str.match(r"^\d{6}$").all():
                try:
                    df_global[col] = pd.to_datetime(s, format="%Y%m")
                except:
                    pass

        df_global = df_global.dropna(axis=1, how="all")
        df_global = df_global.dropna(axis=0, how="all")

    except Exception as e:
        return render_template("home.html", error=f"Error reading CSV: {str(e)}")

    # ⚠️ FIXED: This keeps CSV + shows buttons
    return redirect(url_for("home", uploaded=1))


# -------------------------------------------------------
# HISTOGRAM
# -------------------------------------------------------
@app.route("/histogram", methods=["GET", "POST"])
def histogram():
    global df_global
    if df_global is None:
        return redirect(url_for("home"))

    numeric_cols = df_global.select_dtypes(include=["int64", "float64"]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if "id" not in c.lower()]

    if request.method == "GET":
        return render_template("histogram.html", columns=numeric_cols)

    column = request.form.get("column")
    values = df_global[column].dropna()
    max_val = values.max()

    scale = 1
    suffix = ""
    if max_val > 1_000_000:
        scale = 1_000_000
        suffix = " (Millions)"
    elif max_val > 1_000:
        scale = 1_000
        suffix = " (Thousands)"

    scaled = values / scale
    unique_vals = scaled.nunique()

    # Smart bin logic
    if unique_vals <= 30:
        bins = unique_vals
    elif unique_vals <= 200:
        bins = int(unique_vals ** 0.5)
    else:
        q75, q25 = np.percentile(scaled, [75, 25])
        iqr = q75 - q25
        bin_size = 2 * iqr / (len(scaled) ** (1/3)) if iqr > 0 else 1
        bins = max(10, min(int((scaled.max() - scaled.min()) / bin_size), 75))

    # MATCH PIE COLOR SCHEME
    cmap = plt.cm.Blues
    color = cmap(0.55)   # medium–light pie slice shade

    fig, ax = plt.subplots()
    ax.hist(scaled, bins=bins, edgecolor="black", color=color)

    pretty = column.replace("_", " ").title()
    ax.set_xlabel(pretty + suffix)
    ax.set_ylabel("Frequency")
    ax.set_title(f"Distribution of {pretty}")
    ax.xaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.2f}"))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()

    return render_template("histogram.html", columns=numeric_cols,
                           image=encoded, selected_col=column)


# -------------------------------------------------------
# BAR CHART
# -------------------------------------------------------
@app.route("/bar", methods=["GET", "POST"])
def bar():
    global df_global
    if df_global is None:
        return redirect(url_for("home"))

    categorical_cols = [
        c for c in df_global.select_dtypes(include=["object"]).columns
        if df_global[c].nunique() <= 30
        and "id" not in c.lower()
        and "date" not in c.lower()
        and c.lower() not in ["comments", "comment"]
    ]

    if request.method == "GET":
        return render_template("bar.html", columns=categorical_cols)

    col = request.form.get("column")
    counts = df_global[col].value_counts()

    cmap = plt.cm.Blues
    colors = cmap(np.linspace(0.35, 0.95, len(counts)))  # MATCH PIE

    fig, ax = plt.subplots()
    ax.bar(counts.index.astype(str), counts.values,
           edgecolor="black", color=colors)

    pretty = col.replace("_", " ").title()
    ax.set_title(f"Bar Chart of {pretty}")
    ax.set_xlabel(pretty)
    ax.set_ylabel("Count")

    if len(counts.index) > 6:
        plt.xticks(rotation=45)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()

    return render_template("bar.html", columns=categorical_cols,
                           image=encoded, selected_col=col)


# -------------------------------------------------------
# SCATTER PLOT
# -------------------------------------------------------
@app.route("/scatter", methods=["GET", "POST"])
def scatter():
    global df_global
    if df_global is None:
        return redirect(url_for("home"))

    numeric_cols = df_global.select_dtypes(include=["int64", "float64"]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if "id" not in c.lower()]

    if request.method == "GET":
        return render_template("scatter.html", columns=numeric_cols)

    x = request.form.get("x_column")
    y = request.form.get("y_column")

    # MATCH PIE — use darkest Blues slice
    cmap = plt.cm.Blues
    dot_color = cmap(0.90)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df_global[x], df_global[y],
               edgecolor="black", color=dot_color)

    ax.set_xlabel(x.replace("_", " ").title())
    ax.set_ylabel(y.replace("_", " ").title())
    ax.set_title(f"{y.replace('_',' ').title()} vs {x.replace('_',' ').title()}")

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()

    return render_template("scatter.html",
                           columns=numeric_cols,
                           image=encoded,
                           x_col_selected=x,
                           y_col_selected=y)


# -------------------------------------------------------
# PIE CHART
# -------------------------------------------------------
@app.route("/pie", methods=["GET", "POST"])
def pie():
    global df_global
    if df_global is None:
        return redirect(url_for("home"))

    categorical_cols = [
        c for c in df_global.select_dtypes(include=["object"]).columns
        if df_global[c].nunique() <= 30
        and "id" not in c.lower()
        and "date" not in c.lower()
    ]

    if request.method == "GET":
        return render_template("pie.html", columns=categorical_cols)

    col = request.form.get("column")
    counts = df_global[col].value_counts(dropna=False)

    labels = counts.index.tolist()
    values = counts.values
    pretty = col.replace("_", " ").title()

    cmap = plt.cm.Blues
    colors = cmap(np.linspace(0.35, 0.95, len(values)))

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _ = ax.pie(values,
                       startangle=90,
                       wedgeprops={"edgecolor": "black"},
                       colors=colors)

    ax.set_title(f"Distribution of {pretty}")
    ax.axis("equal")
    ax.legend(wedges, labels, title=pretty,
              loc="center left", bbox_to_anchor=(1, 0.5))

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode()

    return render_template("pie.html", columns=categorical_cols,
                           image=encoded, selected_col=col)


# -------------------------------------------------------
# RUN
# -------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
