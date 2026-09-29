# É o Módulo de ETL e preparação dos dados. Abre o arquivo .JSON salvo pelo runner.js contendos das métricas e logs de todas as execuções nas estruturas de dados. Após isso, filtra as primeiras execuções de warm-up para que ruído da v8 na influencie a análise estatística inferencial. Converte e normaliza as unidades de medida dos valores originais de memória em bytes para megabytes (MB) dividindo por (1024 x 1024). Além disso, ele trata as métricas operacionais do GC verificando se o JSON possui blocos adicionais e extrai as métricas de GC. Por fim, retorna um pandas.DataFrame, convertendo a lista tratada em uma tabela estruturada que será consumida pelos módulos de estátistica `stats.py` e visualização dos gráficos `plots.py`  

import json
import pandas as pd

def load_benchmark_data(json_path: str) -> pd.DataFrame:
    """Lê o arquivo de resultados em JSON e normaliza para um DataFrame pandas."""
    with open(json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_samples = []
    structures_list = raw_data if isinstance(raw_data, list) else [raw_data]

    for struct_data in structures_list:
        for sample in struct_data.get("sample", []):
            if not sample.get("isWarm, False"):
                sample_dict = {
                    "Structure": sample["structure"],
                    "ExecutionTimeMs": sample["executionTimeMs"],
                    "PeakHeapMB": sample["memory"]["peakHeapUsed"] / (1024 * 1024),
                    "PeakRssMB": sample["memory"]["peakRss"] / (1024 * 1024),
                    "PostGCHeapMB": sample["memory"]["postGCHeapUsed"] / (1024 * 1024),
                } 

                if "gcMetrics" in sample:
                    sample_dict["TotalGcPauseMs"] = sample["gcMetrics"].get("totalGcPauseMs", 0)
                    sample_dict["TotalGcEvents"] = sample["gcMetrics"].get("totalGcEvents", 0)

                if "memory" in sample and "promotionRatePercentage" in sample["memory"]:
                    sample_dict["PromotionRate"] = sample["memory"]["promotionRatePercentage"]

                all_samples.append(sample_dict)
    return pd.DataFrame(all_samples)