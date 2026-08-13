// src/workloads/execute.js

const ABBStructure = require('../structures/abb');
const ArrayStructure = require('../structures/array');
const MapStructure = require('../structures/map');
const SetStructure = require('../structures/set');

const { getMemorySnapshot, forceGC } = require('../utils/memory');

const args = process.argv.slice(2);
const structureType = args[0] ? args[0].toLowerCase() : 'array';

const WORKLOAD_SIZE = 100000

function runBenchmark() {
  forceGC();
  const initialMemory = getMemorySnapshot();

  let structure;
  
  if(structureType === 'map') {
    structure = new MapStructure();
  } else if(structureType === 'set') {
    structure = new SetStructure()
  } else if(structureType === 'abb') {
    structure = new ABBStructure();
  } else {
    structure = new ArrayStructure();
  }

  const startTime = process.hrtime.bigint();

  for (let i = 0; i < WORKLOAD_SIZE; i++) {
    structure.insert(`key_${i}`, { id: i, data: `payload_${i}` });
  }

  const endTime = process.hrtime.bigint();
  const executionTimeMs = Number(endTime - startTime) / 1e6;
  const peakMemory = getMemorySnapshot();

  structure.clear();
  const postClearMemory = getMemorySnapshot();

  forceGC();
  const postGCMemory = getMemorySnapshot();

  const report = {
    structure: structureType.charAt(0).toUpperCase() + structureType.slice(1),
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