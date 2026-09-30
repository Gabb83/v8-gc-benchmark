import numpy as np
import pandas as pd
import scipy.stats as stats
import scikit_posthocs as sp

def get_descriptive_stats(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Calcula estatísticas descritivas (Média, Mediana, DP, P99)."""
    return (
        df.groupby("Structure")[metric]
        .agg(
            Média="mean",
            Mediana="median",
            DesvioPadrão="std",
            P99=lambda x: np.percentile(x, 99),
        )
        .reset_index()
    )

def run_hypothesis_pipeline(df: pd.DataFrame, metric: str):
    """Executa checagem de variabilidade, Shapiro-Wilk e Kruskal-Wallis."""
    groups_dict = {
        group: group_df[metric].dropna().values
        for group, group_df in df.groupby("Structure")
    }

    if len(groups_dict) < 2:
        return None

    #1 checagem de variabilidade intra-grupo
    constant_groups = [g for g, v in groups_dict.items() if len(np.unique(v)) <= 1]
    
    if len(constant_groups) == len(groups_dict):
        return {"test": "Constant", "significant": False}

    #2 shapiro-Wilk (verificação de normalidade)
    is_normal = True
    for group, values in groups_dict.items():
        if len(np.unique(values)) > 1:
            _, p_val = stats.shapiro(values)
            if p_val <= 0.05:
                is_normal = False

    #3 teste global (kruskal-Wwllis)
    groups = list(groups_dict.values())
    stat, p_val = stats.kruskal(*groups)
    
    return {
        "test": "Kruskal-Wallis",
        "statistic": stat,
        "p_value": p_val,
        "significant": p_val < 0.05
    }

def run_dunn_posthoc(df: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Executa o teste post-hoc de Dunn com ajuste de Bonferroni."""
    return sp.posthoc_dunn(
        df,
        val_col=metric,
        group_col="Structure",
        p_adjust="bonferroni"
    )