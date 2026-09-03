import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as sp
import seaborn as sns

# Configuração visual profissional para relatórios acadêmicos
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({"font.size": 12, "figure.dpi": 150})


# 1. Carregar e Processar os Dados (Incluindo Métricas do GC)
def load_data(json_filename="results_full_suite.json"):
    with open(json_filename, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_samples = []
    structures_list = raw_data if isinstance(raw_data, list) else [raw_data]

    for struct_data in structures_list:
        for sample in struct_data.get("samples", []):
            if not sample.get("isWarmup", False):
                # Extração das métricas legadas e novas métricas de GC
                sample_dict = {
                    "Structure": sample["structure"],
                    "ExecutionTimeMs": sample["executionTimeMs"],
                    "PeakHeapMB": sample["memory"]["peakHeapUsed"]
                    / (1024 * 1024),
                    "PeakRssMB": sample["memory"]["peakRss"] / (1024 * 1024),
                    "PostGCHeapMB": sample["memory"]["postGCHeapUsed"]
                    / (1024 * 1024),
                }

                # Suporte para o novo bloco de métricas do GC (se presente no JSON)
                if "gcMetrics" in sample:
                    sample_dict["TotalGcPauseMs"] = sample["gcMetrics"].get(
                        "totalGcPauseMs", 0
                    )
                    sample_dict["TotalGcEvents"] = sample["gcMetrics"].get(
                        "totalGcEvents", 0
                    )
                if "memory" in sample and "promotionRatePercentage" in sample[
                    "memory"
                ]:
                    sample_dict["PromotionRate"] = sample["memory"][
                        "promotionRatePercentage"
                    ]

                all_samples.append(sample_dict)

    return pd.DataFrame(all_samples)


df = load_data("results_full_suite.json")


# 2. Função de Estatística Descritiva
def show_descriptive_stats(df, metric):
    print(f"\n========================================================")
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


# 3. Função de Testes de Hipóteses (Shapiro-Wilk + Kruskal-Wallis / ANOVA)
def run_hypothesis_tests(df, metric):
    print("\n--------------------------------------------------------")
    print(f"       TESTES ESTATÍSTICOS DE HIPÓTESES: {metric}")
    print("--------------------------------------------------------")

    groups_dict = {
        group: group_df[metric].dropna().values
        for group, group_df in df.groupby("Structure")
    }

    # Verifica se existem dados suficientes
    if len(groups_dict) < 2:
        print("Dados insuficientes para comparação entre estruturas.")
        return None

    # -----------------------------------------------------
    # 1. Verificação de variabilidade
    # -----------------------------------------------------
    print("[1] Verificação de Variabilidade:")

    constant_groups = []

    for group, values in groups_dict.items():
        unique_values = np.unique(values)

        if len(unique_values) <= 1:
            constant_groups.append(group)

        print(
            f" - {group:10s}: "
            f"n = {len(values):3d} | "
            f"valores distintos = {len(unique_values)}"
        )

    # Caso especial: todos os grupos são constantes
    if len(constant_groups) == len(groups_dict):
        print("\n[2] Teste Inferencial:")
        print(
            " - Todas as estruturas possuem valores constantes dentro "
            "dos grupos."
        )
        print(
            " - Não é apropriado aplicar Shapiro-Wilk ou ANOVA neste caso."
        )

        # Verifica se os valores entre as estruturas são diferentes
        group_values = {
            group: values[0] for group, values in groups_dict.items()
        }

        print("\nValores observados por estrutura:")
        for group, value in group_values.items():
            print(f" - {group:10s}: {value}")

        if len(set(group_values.values())) > 1:
            print(
                "\nConclusão: os valores são diferentes entre as estruturas, "
                "mas não há variabilidade intraestrutura suficiente para "
                "realizar um teste inferencial convencional."
            )
        else:
            print(
                "\nConclusão: todas as estruturas apresentam o mesmo valor."
            )

        return {
            "test": None,
            "statistic": None,
            "p_value": None,
            "significant": None,
        }

    # -----------------------------------------------------
    # 2. Shapiro-Wilk
    # -----------------------------------------------------
    print("\n[2] Teste de Normalidade (Shapiro-Wilk):")

    is_normal = True

    for group, values in groups_dict.items():

        # Shapiro não deve ser aplicado a grupo constante
        if len(np.unique(values)) <= 1:
            print(
                f" - {group:10s}: grupo constante "
                f"(Shapiro-Wilk não aplicável)"
            )
            is_normal = False
            continue

        stat, p_val = stats.shapiro(values)

        status = "Normal" if p_val > 0.05 else "Não-Normal"

        print(
            f" - {group:10s}: "
            f"W = {stat:.5f} | "
            f"p-value = {p_val:.5f} ({status})"
        )

        if p_val <= 0.05:
            is_normal = False

    groups = list(groups_dict.values())

    # -----------------------------------------------------
    # 3. Teste global
    # -----------------------------------------------------
    print("\n[3] Teste Inferencial:")

    # Para este benchmark, usamos Kruskal-Wallis como teste
    # global robusto para as métricas contínuas.
    stat, p_val = stats.kruskal(*groups)

    print(" - Teste aplicado: Kruskal-Wallis")
    print(f" - H-statistic: {stat:.4f}")
    print(f" - p-value: {p_val:.5e}")

    if p_val < 0.05:
        print(
            "\nConclusão: há diferença estatisticamente significativa "
            "entre as estruturas (rejeita-se H0)."
        )
        significant = True
    else:
        print(
            "\nConclusão: não há diferença estatisticamente significativa "
            "entre as estruturas (não se rejeita H0)."
        )
        significant = False

    return {
        "test": "Kruskal-Wallis",
        "statistic": stat,
        "p_value": p_val,
        "significant": significant,
    }


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


# --- MAPA COMPLETO DE MÉTRICAS (ANTIGAS + NOVAS DO GC) ---
metrics_map = {
    "ExecutionTimeMs": "Tempo de Execução (ms)",
    "PeakHeapMB": "Pico de Uso da Heap (MB)",
    "PeakRssMB": "Pico de Uso de RSS (MB)",
}

# Adiciona dinamicamente as novas métricas de GC se existirem no DataFrame
if "TotalGcPauseMs" in df.columns:
    metrics_map["TotalGcPauseMs"] = "Tempo Total de Pausa do GC (ms)"
if "TotalGcEvents" in df.columns:
    metrics_map["TotalGcEvents"] = "Total de Eventos de GC"
if "PromotionRate" in df.columns:
    metrics_map["PromotionRate"] = "Taxa de Promoção para Old Space (%)"

# --- EXECUÇÃO PIPELINE ESTATÍSTICO ---
# --- EXECUÇÃO PIPELINE ESTATÍSTICO ---
for metric_key, metric_label in metrics_map.items():

    if metric_key not in df.columns:
        continue

    # Estatística descritiva
    show_descriptive_stats(df, metric_key)

    # Teste global
    test_result = run_hypothesis_tests(df, metric_key)

    # -----------------------------------------------------
    # Dunn somente quando:
    # 1. existe teste global
    # 2. o resultado global foi significativo
    # -----------------------------------------------------
    if (
        test_result is not None
        and test_result["test"] == "Kruskal-Wallis"
        and test_result["significant"]
    ):
        dunn_result = sp.posthoc_dunn(
            df,
            val_col=metric_key,
            group_col="Structure",
            p_adjust="bonferroni",
        )

        print("\n========================================================")
        print(
            f"   TESTE POST-HOC DE DUNN: "
            f"{metric_label} (P-Values Ajustados)"
        )
        print("========================================================")
        print(dunn_result.round(6).to_string())

    elif metric_key == "TotalGcEvents":
        print("\n--------------------------------------------------------")
        print("Dunn não aplicado para TotalGcEvents.")
        print(
            "Motivo: os grupos apresentam valores constantes, "
            "sem variabilidade intraestrutura."
        )