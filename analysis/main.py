import os
import sys

#ajusta os caminhos de importação e raiz do repo
analysis_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(analysis_dir)

if analysis_dir not in sys.path:
    sys.path.append(analysis_dir)

from src.loader import load_benchmark_data
from src.stats import get_descriptive_stats, run_hypothesis_pipeline, run_dunn_posthoc
from src.plots import plot_and_save_metric

def main():
    json_path = os.path.join(root_dir, "data", "raw", "results_full_suite.json")
    output_plots_dir = os.path.join(root_dir, "data", "processed", "plots")

    if not os.path.exists(json_path):
        print(f"\nERRO: Arquivo JSON não encontrado em: {json_path}")
        return

    print(f"📂 Carregando dados de: {json_path}")
    df = load_benchmark_data(json_path)

    if df.empty:
        print("ERRO: O DataFrame carregado está vazio!")
        return

    print(f"Dados carregados com sucesso! Linhas: {len(df)} | Colunas: {list(df.columns)}")

    # Mapeamento com lista de possíveis nomes para cada métrica no DataFrame
    metrics_config = [
        {
            "candidates": ["ExecutionTimeMs", "executionTimeMs"],
            "ylabel": "Tempo de Execução (ms)",
            "title": "Tempo de Execução por Estrutura"
        },
        {
            "candidates": ["PeakHeapMB", "peakHeapMB", "peakHeapUsed"],
            "ylabel": "Pico de Uso da Heap (MB)",
            "title": "Pico de Consumo da Heap"
        },
        {
            "candidates": ["PeakRssMB", "peakRssMB", "peakRss"],
            "ylabel": "Pico de Uso de RSS (MB)",
            "title": "Pico de Consumo da Memória RSS"
        },
        {
            "candidates": ["TotalGcPauseMs", "totalGcPauseMs"],
            "ylabel": "Tempo Total de Pausa do GC (ms)",
            "title": "Pausa do GC"
        },
        {
            "candidates": ["TotalGcEvents", "totalGcEvents"],
            "ylabel": "Total de Eventos de GC",
            "title": "Frequência do GC"
        },
        {
            "candidates": ["PromotionRate", "promotionRate"],
            "ylabel": "Taxa de Promoção (%)",
            "title": "Taxa de Promoção para Old Space"
        }
    ]

    metrics_processed = 0

    for item in metrics_config:
        #encontra qual dos nomes candidatos existe nas colunas do DataFrame
        metric_key = next((col for col in item["candidates"] if col in df.columns), None)

        if not metric_key:
            continue

        metrics_processed += 1
        ylabel = item["ylabel"]
        title = item["title"]

        print(f"\n========================================================")
        print(f"       PROCESSANDO MÉTRICA: {metric_key}")
        print(f"========================================================")

        #1 estatistica descritiva
        desc_df = get_descriptive_stats(df, metric_key)
        print(desc_df.to_string(index=False))

        #2 Teste de hipoteses (Shapiro / Kruskal-Wallis)
        res = run_hypothesis_pipeline(df, metric_key)

        #IMPRESSÃO DA NORMALIDADE (Shapiro-Wilk)
        if isinstance(res, dict) and "shapiro_results" in res:
            print("\n--- TESTE DE NORMALIDADE DE SHAPIRO-WILK ---")
            shapiro_df = pd.DataFrame(res["shapiro_results"])
            print(shapiro_df.to_string(index=False))

        #IMPRESSÃO DO TESTE GLOBAL (Kruskal-Wallis / ANOVA)
        if isinstance(res, dict) and "test" in res:
            print(f"\n--- TESTE GLOBAL: {res['test'].upper()} ---")
            print(f"Estatística (H/F): {res.get('statistic', 0):.4f}")
            print(f"p-value:          {res.get('p_value', 0):.6e}")
            print(f"Significativo:    {'SIM (p < 0.05)' if res.get('significant') else 'NÃO'}")
        
        #3 post-hoc se o teste global for significativo
        if isinstance(res, dict) and res.get("test") == "Kruskal-Wallis" and res.get("significant"):
            dunn = run_dunn_posthoc(df, metric_key)
            print("\n--- POST-HOC DE DUNN (P-Values Ajustados) ---")
            print(dunn.round(6).to_string())
        
        #4 salva
        plot_and_save_metric(df, metric_key, ylabel, title, output_dir=output_plots_dir)

    if metrics_processed == 0:
        print("\nNenhuma das métricas mapeadas foi encontrada no DataFrame.")
        print(f"Colunas disponíveis: {list(df.columns)}")

if __name__ == "__main__":
    main()