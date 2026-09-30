import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 12, "figure.dpi": 150})

def plot_and_save_metric(df: pd.DataFrame, metric: str, ylabel: str, title: str, output_dir: str = None):
    """Gera gráfico de barras com desvio padrão e salva o PNG se informado o diretório."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    order = df.groupby("Structure")[metric].mean().sort_values().index
    palette = sns.color_palette("mako", n_colors=len(order))
    
    bars = sns.barplot(
        x="Structure", y=metric, hue="Structure", data=df,
        order=order, palette=palette, errorbar="sd", capsize=0.1,
        err_kws={"linewidth": 1.5, "color": "black"}, ax=ax
    )

    for p in bars.patches:
        height = p.get_height()
        if not np.isnan(height) and height > 0:
            ax.annotate(
                f"{height:.2f}",
                (p.get_x() + p.get_width() / 2.0, height),
                ha="center", va="bottom", fontsize=11, fontweight="bold",
                color="#222222", xytext=(0, 5), textcoords="offset points"
            )

    max_val = df.groupby("Structure")[metric].mean().max()
    ax.set_ylim(0, max_val * 1.18)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#111111")
    ax.set_xlabel("Estrutura de Dados", fontsize=12, labelpad=10, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=12, labelpad=10, fontweight="bold")

    sns.despine(top=True, right=True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)
    plt.tight_layout()

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{metric}.png")
        plt.savefig(file_path, bbox_inches="tight")
        print(f"Gráfico salvo em: {file_path}")

    plt.close()