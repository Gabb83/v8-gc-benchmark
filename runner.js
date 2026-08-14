// runner.js

const { execSync } = require('child_process');
const STRUCTURES = ['array', 'map', 'set', 'abb', 'avl'];

console.log('INICIANDO TESTES AUTOMATIZADOS ...');

STRUCTURES.forEach((structure) => {
  console.log(`EXECUTANDO: ${structure.toUpperCase()}`);

  try {
    const output = execSync(`node --expose-gc --trace-gc src/workloads/execute.js ${structure}`, {encoding: 'utf-8'});
    console.log(output);
  } catch(error) {
    console.error(`erro ao executar estrutura ${structure}`, error.message);
  }
});

console.log('TESTES CONCLUÍDOS');