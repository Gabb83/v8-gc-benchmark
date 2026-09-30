const { PerformanceObserver, performance, constants } = require('perf_hooks');
const v8 = require('v8');
const { setTimeout: sleep } = require('timers/promises');

const ABBStructure = require('../structures/abb');
const ArrayStructure = require('../structures/array');
const AVLStructure = require('../structures/avl');
const MapStructure = require('../structures/map');
const SetStructure = require('../structures/set');

const { getMemorySnapshot, forceGC } = require('../utils/memory');

const gcEntries = [];

const obs = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  gcEntries.push(...entries);
});

obs.observe({ entryTypes: ['gc'], buffered: true });

const args = process.argv.slice(2);
const structureType = args[0] ? args[0].toLowerCase() : 'array';
const WORKLOAD_SIZE = 100000;

async function runBenchmark() {
  forceGC();
  performance.clearMarks();

  const initialMemory = getMemorySnapshot();
  const initialSpaces = v8.getHeapSpaceStatistics();
  const initialOldSpace =
    initialSpaces.find((s) => s.space_name === 'old_space')?.space_used_size || 0;

  performance.mark('benchmark-start');

  let structure;
  if (structureType === 'map') structure = new MapStructure();
  else if (structureType === 'set') structure = new SetStructure();
  else if (structureType === 'abb') structure = new ABBStructure();
  else if (structureType === 'avl') structure = new AVLStructure();
  else structure = new ArrayStructure();

  const startTime = process.hrtime.bigint();

  for (let i = 0; i < WORKLOAD_SIZE; i++) {
    structure.insert(`key_${i}`, { id: i, data: `payload_${i}` });
  }

  const endTime = process.hrtime.bigint();
  const executionTimeMs = Number(endTime - startTime) / 1e6;

  performance.mark('benchmark-end');

  const peakMemory = getMemorySnapshot();
  const finalSpaces = v8.getHeapSpaceStatistics();
  const finalOldSpace =
    finalSpaces.find((s) => s.space_name === 'old_space')?.space_used_size || 0;

  structure.clear();
  const postClearMemory = getMemorySnapshot();

  forceGC();
  const postGCMemory = getMemorySnapshot();
  await sleep(100);

  let minorGcCount = 0;
  let majorGcCount = 0;
  let totalGcPauseMs = 0;
  const gcPauses = [];

  gcEntries.forEach((entry) => {
    const duration = entry.duration;
    totalGcPauseMs += duration;
    gcPauses.push(duration);

    const gcKind = entry.detail ? entry.detail.kind : entry.kind;

    if (
      gcKind === constants.NODE_PERFORMANCE_GC_MAJOR ||
      gcKind === constants.NODE_PERFORMANCE_GC_INCREMENTAL ||
      gcKind === constants.NODE_PERFORMANCE_GC_WEAKCB
    ) {
      majorGcCount++;
    } else {
      minorGcCount++;
    }
  });

  const allocatedBytes = Math.max(0, peakMemory.heapUsed - initialMemory.heapUsed);
  const promotedBytes = Math.max(0, finalOldSpace - initialOldSpace);
  const totalGcEvents = gcEntries.length;
  const executionTimeSec = executionTimeMs / 1000;

  const report = {
    structure: structureType.charAt(0).toUpperCase() + structureType.slice(1),
    elements: WORKLOAD_SIZE,
    executionTimeMs,
    memory: {
      initialHeapUsed: initialMemory.heapUsed,
      peakHeapUsed: peakMemory.heapUsed,
      peakRss: peakMemory.rss,
      postClearHeapUsed: postClearMemory.heapUsed,
      postGCHeapUsed: postGCMemory.heapUsed,
      allocatedBytes,
      promotedToOldSpaceBytes: promotedBytes,
      promotionRatePercentage:
        allocatedBytes > 0
          ? parseFloat(((promotedBytes / allocatedBytes) * 100).toFixed(2))
          : 0,
    },
    gcMetrics: {
      totalGcEvents,
      minorGcCount,
      majorGcCount,
      totalGcPauseMs: parseFloat(totalGcPauseMs.toFixed(3)),
      avgGcPauseMs:
        gcPauses.length > 0 ? parseFloat((totalGcPauseMs / gcPauses.length).toFixed(3)) : 0,
      maxGcPauseMs:
        gcPauses.length > 0 ? parseFloat(Math.max(...gcPauses).toFixed(3)) : 0,
    },
    throughput: {
      elementsPerSecond:
        executionTimeSec > 0 ? parseFloat((WORKLOAD_SIZE / executionTimeSec).toFixed(2)) : 0,
      megabytesPerSecond:
        executionTimeSec > 0
          ? parseFloat(((allocatedBytes / (1024 * 1024)) / executionTimeSec).toFixed(2))
          : 0,
    },
  };

  console.log(JSON.stringify(report, null, 2));

  obs.disconnect();
  process.exit(0);
}

runBenchmark().catch((err) => {
  console.error(err);
  process.exit(1);
});