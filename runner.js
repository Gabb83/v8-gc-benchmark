const { execSync } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

const STRUCTURES = ['array', 'map', 'set', 'abb', 'avl'];
const WARMUP_RUNS = 10;
const VALID_RUNS = 30;

function showHeaderMenu() {
  console.log('\n================================================================');
  console.log('           ⚡ V8 GARBAGE COLLECTION BENCHMARK RUNNER ⚡           ');
  console.log('================================================================');

  console.log('Selecione o modo de execução: \n');
  console.log('[1] | Bateria completa (40 execuções: 10 warm-up (descartadas) + 30 válidas)');
  console.log('[2] | Teste piloto (1 execução sem warm-up)');
  console.log('[0] | Sair');
  console.log('----------------------------------------------------------------');
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

showHeaderMenu();

rl.question('Digite uma opção [1, 2 ou 0]: ', (answer) => {
  let isFullSuite;

  switch(answer.trim()) {
    case '1': {
      isFullSuite = true;
      break;
    }
    case '2': {
      isFullSuite = false;
      break;
    }
    case '0': {
      console.log('\nOperação cancelada. Saindo...\n');
      rl.close();
      process.exit(0);
    } 
    default: {
      console.log('\nOperação inválida. Saindo...\n');
      rl.close();
      process.exit(1);
    }
  }

  const totalRuns = isFullSuite ? (WARMUP_RUNS + VALID_RUNS) : 1;

  console.log('\n==================================================');
  console.log(` MODO: ${isFullSuite ? 'BATERIA COMPLETA (40x)' : 'EXECUÇÃO ÚNICA / PILOTO (1x)'}`);
  console.log('==================================================\n');

  const allResults = [];

  STRUCTURES.forEach((structure) => {
    console.log(`\nEXECUTANDO: ${structure.toUpperCase()}`);
    const structureResults = [];

    for(let run = 1; run <= totalRuns; run++) {
      const isWarmup = isFullSuite && run <= WARMUP_RUNS;
      const statusLabel = isWarmup ? `[WARM-UP ${run}/${WARMUP_RUNS}]` : `[AMOSTRA VÁLIDA ${isFullSuite ? run - WARMUP_RUNS : 1}]`;

      console.log(`-> Execução ${run}/${totalRuns} ${statusLabel}`);

      try {
        const output = execSync(
          `node --expose-gc --trace-gc src/workloads/execute.js ${structure}`,
          { encoding: 'utf-8' }
        );

        console.log(output);

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

  const outputDir = path.join(__dirname, 'data', 'raw');
  if(!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const fileName = isFullSuite? 'results_full_suite.json' : 'results_pilot_run.json';
  const outputPath = path.join(outputDir, fileName);

  fs.writeFileSync(outputPath, JSON.stringify(allResults, null, 2));

  console.log('\n==================================================');
  console.log(` TESTES CONCLUÍDOS! Dados salvos em: ${outputPath}`);
  console.log('==================================================\n');

  rl.close();
});