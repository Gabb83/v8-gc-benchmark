const { execSync } = require('child_process');
const readline = require('readline');
const fs = require('fs');

const STRUCTURES = ['array', 'map', 'set', 'abb', 'avl'];
const WARMUP_RUNS = 10;
const VALID_RUNS = 30;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('Deseja executar a Bateria Completa (40 execuções com Warm-up)? [S/N]: ', (answer) => {
  const isFullSuite = answer.trim().toUpperCase() === 'S';
  const totalRuns = isFullSuite ? (WARMUP_RUNS + VALID_RUNS) : 1;

  console.log('\n==================================================');
  console.log(` MODO: ${isFullSuite ? 'BATERIA COMPLETA (40x)' : 'EXECUÇÃO ÚNICA / PILOTO (1x)'}`);
  console.log('==================================================\n');

  const allResults = [];

  STRUCTURES.forEach((structure) => {
    console.log(`\nEXECUTANDO: ${structure.toUpperCase()}`);
    const structureResults = [];

    for (let run = 1; run <= totalRuns; run++) {
      const isWarmup = isFullSuite && run <= WARMUP_RUNS;
      const statusLabel = isWarmup ? `[WARM-UP ${run}/${WARMUP_RUNS}]` : `[AMOSTRA VÁLIDA ${isFullSuite ? run - WARMUP_RUNS : 1}]`;

      console.log(`-> Execução ${run}/${totalRuns} ${statusLabel}`);

      try {
        const output = execSync(
          `node --expose-gc --trace-gc src/workloads/execute.js ${structure}`,
          { encoding: 'utf-8' }
        );

        // Exibe os logs do trace-gc no terminal
        console.log(output);

        // Extrai e armazena o JSON do relatório impresso pelo execute.js
        const jsonMatch = output.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const report = JSON.parse(jsonMatch[0]);
          report.runNumber = run;
          report.isWarmup = isWarmup;

          if (!isWarmup) {
            structureResults.push(report);
          }
        }
      } catch (error) {
        console.error(`Erro ao executar estrutura ${structure}:`, error.message);
      }
    }

    allResults.push({
      structure,
      totalRunsExecuted: totalRuns,
      validSamplesCount: structureResults.length,
      samples: structureResults
    });
  });

  // Salva o resultado consolidado em JSON para leitura posterior via Python
  const outputFile = isFullSuite ? 'results_full_suite.json' : 'results_pilot_run.json';
  fs.writeFileSync(outputFile, JSON.stringify(allResults, null, 2));

  console.log('\n==================================================');
  console.log(` TESTES CONCLUÍDOS! Dados salvos em: ${outputFile}`);
  console.log('==================================================\n');

  rl.close();
});