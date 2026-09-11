const ABBStructure = require('./structures/abb');
const abb = new ABBStructure();

for (let i = 0; i < 100000; i++) {
  abb.insert(`key_${i}`, { id: i, data: `payload_${i}` });
}

console.log(`Altura da ABB após 100k elementos: ${abb.getAltura()}`);