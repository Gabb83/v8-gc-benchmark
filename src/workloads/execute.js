// src/workloads/execute.js

const ArrayStructure = require('../structures/array');
const { getMemorySnapshot, forceGC } = require('../utils/memory');

const WORKLOAD_SIZE = 100000

function runBenchmark() {
  forceGC();

  const initialMemory = getMemorySnapshot();

  const structure = new ArrayStructure();

  // 2. Carga de trabalho: inserção de 100.000 elementos[cite: 1]
  const startTime = process.hrtime.bigint();

  for (let i = 0; i < WORKLOAD_SIZE; i++) {
    structure.insert(`key_${i}`, { id: i, data: `payload_${i}` });
  }

  const endTime = process.hrtime.bigint();
  const executionTimeMs = Number(endTime - startTime) / 1e6; // Converte nanosegundos para ms

  // 3. Captura do pico de memória alocada[cite: 1]
  const peakMemory = getMemorySnapshot();

  // 4. Limpeza da estrutura e verificação de desalocação
  structure.clear();
  const postClearMemory = getMemorySnapshot();

  // Força o GC para observar o comportamento de descarte da V8[cite: 1]
  forceGC();
  const postGCMemory = getMemorySnapshot();

  // 5. Montagem do relatório individual da execução
  const report = {
    structure: 'Array',
    elements: WORKLOAD_SIZE,
    executionTimeMs,
    memory: {
      initialHeapUsed: initialMemory.heapUsed,
      peakHeapUsed: peakMemory.heapUsed,
      peakRss: peakMemory.rss,
      postClearHeapUsed: postClearMemory.heapUsed,
      postGCHeapUsed: postGCMemory.heapUsed
    }
  };

  console.log(JSON.stringify(report, null, 2));
}

runBenchmark();