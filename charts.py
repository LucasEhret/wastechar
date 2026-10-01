"""Material comparison charts shared by the dashboard and PDF report."""

import textwrap

from matplotlib.figure import Figure
import pandas as pd


def material_bar_chart(summary: pd.DataFrame, title: str, axis_label: str) -> Figure:
    rows = summary.sort_values("Poids net", ascending=False, kind="stable")
    labels = [textwrap.fill(str(value), width=32) for value in rows["Classe de matériau"]]
    height = max(3.0, 1.2 + sum(max(1, label.count("\n") + 1) for label in labels) * 0.35)
    figure = Figure(figsize=(10, height), layout="constrained")
    ax = figure.subplots()
    bars = ax.barh(range(len(rows)), rows["Poids net"], color="#2DC5A2")
    ax.set_yticks(range(len(rows)), labels)
    ax.invert_yaxis()
    ax.bar_label(bars, labels=[
        f"{weight:.3f} kg ({percentage:.1f}%)"
        for weight, percentage in zip(rows["Poids net"], rows["Pourcentage de la masse totale"])
    ], padding=5, fontsize=9)
    ax.set_xlim(0, max(float(rows["Poids net"].max()), 1.0) * 1.5)
    ax.set_xlabel(axis_label)
    ax.set_title(title)
    ax.set_axisbelow(True)
    ax.grid(axis="x", alpha=0.2)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    return figure
