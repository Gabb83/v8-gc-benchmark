import json
import os
import pandas as pd

def load_benchmark_data(json_filename: str) -> pd.DataFrame:
    """
    Carrega o arquivo JSON do benchmark e converte para um DataFrame Pandas.
    Extrai as métricas de cada objeto dentro do array 'samples'.
    """
    if not os.path.exists(json_filename):
        print(f"Arquivo não encontrado: {json_filename}")
        return pd.DataFrame()

    with open(json_filename, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_samples = []
    structures_list = raw_data if isinstance(raw_data, list) else [raw_data]

    for struct_entry in structures_list:
        #pega a lista de amostras dentro da estrutura
        samples = struct_entry.get("samples", [])
        
        #nome padrão da estrutura
        default_struct = struct_entry.get("structure", "Unknown")

        for sample in samples:
            #garante que não eh warmup (caso venha sinalizado no JSON)
            if sample.get("isWarmup", False):
                continue

            #extração segura das métricas primarias
            struct_name = sample.get("structure", default_struct)
            exec_time = sample.get("executionTimeMs", 0)
            
            memory = sample.get("memory", {})
            peak_heap = memory.get("peakHeapUsed", 0) / (1024 * 1024)
            peak_rss = memory.get("peakRss", 0) / (1024 * 1024)
            post_gc_heap = memory.get("postGCHeapUsed", 0) / (1024 * 1024)

            sample_dict = {
                "Structure": str(struct_name).upper(),
                "ExecutionTimeMs": float(exec_time),
                "PeakHeapMB": float(peak_heap),
                "PeakRssMB": float(peak_rss),
                "PostGCHeapMB": float(post_gc_heap),
            }

            #metricas estendidas do gcMetrics
            if "gcMetrics" in sample:
                gc = sample["gcMetrics"]
                sample_dict["TotalGcPauseMs"] = float(gc.get("totalGcPauseMs", 0))
                sample_dict["TotalGcEvents"] = int(gc.get("totalGcEvents", 0))
                sample_dict["AvgGcPauseMs"] = float(gc.get("avgGcPauseMs", 0))
                sample_dict["MaxGcPauseMs"] = float(gc.get("maxGcPauseMs", 0))

            #taxa de promocao
            if "promotionRatePercentage" in memory:
                sample_dict["PromotionRate"] = float(memory["promotionRatePercentage"])

            all_samples.append(sample_dict)

    df = pd.DataFrame(all_samples)
    return df