const v8 = require('v8');

function getMemorySnapshot() {
  const memoriaUsada = process.memoryUsage();
  const heapStatus = v8.getHeapStatistics();

  return {
    timeStamp: Date.now(),
    rss: memoriaUsada.rss,
    heapTotal: memoriaUsada.heapTotal,
    heapUsed: memoriaUsada.heapUsed,
    external: memoriaUsada.external,
    totalHeapSize: heapStatus.total_heap_size,
    usedHeapSize: heapStatus.used_heap_size,
    heapSizeLimit: heapStatus.heap_size_limit,
    totalAvailableSize: heapStatus.total_available_size
  };
}

function forceGC() {
  if(global.gc) {
    global.gc();
  } else {
    console.warn('Aviso: Garbage Collector não está exposto. Execute com a flag --expose-gc');
  }
} 

module.exports = {
  getMemorySnapshot,
  forceGC
};