import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as sp
import seaborn as sns

# Configuração visual profissional
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 12, "figure.dpi": 150})


# 1. Carregar e Processar os Dados
def load_data(json_filename="results_full_suite.json"):
    with open(json_filename, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_samples = []
    structures_list = (
        raw_data if isinstance(raw_data, list) else [raw_data]
    )

    for struct_data in structures_list:
        for sample in struct_data.get("samples", []):
            if not sample.get("isWarmup", False):
                all_samples.append(
                    {
                        "Structure": sample["structure"],
                        "ExecutionTimeMs": sample["executionTimeMs"],
                        "PeakHeapMB": sample["memory"]["peakHeapUsed"]
                        / (1024 * 1024),
                        "PeakRssMB": sample["memory"]["peakRss"]
                        / (1024 * 1024),
                        "PostGCHeapMB": sample["memory"]["postGCHeapUsed"]
                        / (1024 * 1024),
                    }
                )

    return pd.DataFrame(all_samples)


df = load_data("results_full_suite.json")


# 2. Função de Estatística Descritiva
def show_descriptive_stats(df, metric):
    print(
        f"\n========================================================"
    )
    print(f"       ESTATÍSTICA DESCRITIVA: {metric}")
    print(f"========================================================")
    stats_df = (
        df.groupby("Structure")[metric]
        .agg(
            Média="mean",
            Mediana="median",
            DesvioPadrão="std",
            P99=lambda x: np.percentile(x, 99),
        )
        .reset_index()
    )
    print(stats_df.to_string(index=False))
    return stats_df


# 3. Função de Testes de Hipóteses (Shapiro-Wilk + Kruskal-Wallis)
def run_hypothesis_tests(df, metric):
    print(
        f"\n--------------------------------------------------------"
    )
    print(f"       TESTES ESTATÍSTICOS DE HIPÓTESES: {metric}")
    print(f"--------------------------------------------------------")

    is_normal = True
    print("[1] Teste de Normalidade (Shapiro-Wilk):")
    for group, group_df in df.groupby("Structure"):
        stat, p_val = stats.shapiro(group_df[metric])
        status = "Normal" if p_val > 0.05 else "Não-Normal"
        print(f" - {group:10s}: p-value = {p_val:.5f} ({status})")
        if p_val <= 0.05:
            is_normal = False

    groups = [
        group_df[metric].values for _, group_df in df.groupby("Structure")
    ]

    print("\n[2] Teste Inferencial:")
    if is_normal:
        stat, p_val = stats.f_oneway(*groups)
        print(f" - Dado: Distribuição Normal -> Aplicando ANOVA")
        print(f" - F-statistic: {stat:.4f} | p-value: {p_val:.5e}")
    else:
        stat, p_val = stats.kruskal(*groups)
        print(
            f" - Dado: Distribuição Não-Normal -> Aplicando Kruskal-Wallis"
        )
        print(f" - H-statistic: {stat:.4f} | p-value: {p_val:.5e}")

    if p_val < 0.05:
        print(
            "\nConclusão: Há diferença estatisticamente significativa entre as estruturas (Rejeita H0)."
        )
    else:
        print(
            "\nConclusão: Não há diferença estatisticamente significativa entre as estruturas (Aceita H0)."
        )


# 4. Função para Plotar Gráficos de Barras
def plot_metric(df, metric, ylabel, title):
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    order = df.groupby("Structure")[metric].mean().sort_values().index

    palette = sns.color_palette("mako", n_colors=len(order))
    bars = sns.barplot(
        x="Structure",
        y=metric,
        hue="Structure",
        data=df,
        order=order,
        palette=palette,
        errorbar="sd",
        capsize=0.1,
        err_kws={"linewidth": 1.5, "color": "black"},
        ax=ax,
    )

    for p in bars.patches:
        height = p.get_height()
        if not np.isnan(height) and height > 0:
            ax.annotate(
                f"{height:.2f}",
                (p.get_x() + p.get_width() / 2.0, height),
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
                color="#222222",
                xytext=(0, 5),
                textcoords="offset points",
            )

    max_val = df.groupby("Structure")[metric].mean().max()
    ax.set_ylim(0, max_val * 1.18)

    ax.set_title(title, fontsize=14, fontweight="bold", pad=15, color="#111111")
    ax.set_xlabel(
        "Estrutura de Dados", fontsize=12, labelpad=10, fontweight="bold"
    )
    ax.set_ylabel(ylabel, fontsize=12, labelpad=10, fontweight="bold")

    sns.despine(top=True, right=True)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5, zorder=0)
    ax.set_axisbelow(True)

    plt.tight_layout()
    plt.show()


# --- EXECUÇÃO COMPLETA ---
metrics_map = {
    "ExecutionTimeMs": "Tempo de Execução (ms)",
    "PeakHeapMB": "Pico de Uso da Heap (MB)",
    "PeakRssMB": "Pico de Uso de RSS (MB)",
}

for metric_key, metric_label in metrics_map.items():
    show_descriptive_stats(df, metric_key)
    run_hypothesis_tests(df, metric_key)
    plot_metric(
        df,
        metric_key,
        ylabel=metric_label,
        title=f"Comparativo: {metric_label} por Estrutura",
    )

    # Teste Post-Hoc de Dunn com Bonferroni
    dunn_result = sp.posthoc_dunn(
        df, val_col=metric_key, group_col="Structure", p_adjust="bonferroni"
    )

    print(
        f"\n========================================================"
    )
    print(f"   TESTE POST-HOC DE DUNN: {metric_label} (P-Values)")
    print(f"========================================================")
    print(dunn_result.round(6).to_string())