// src/structures/map.js

class MapStructure {
  constructor() {
    this.data = new Map();
  }

  insert(value) {
    this.data.set(value);
  }

  clear() {
    this.data.clear();
  }

  get size() {
    return this.data.size;
  }
}

// Correção: Adicionado o "s" no exports
module.exports = MapStructure;