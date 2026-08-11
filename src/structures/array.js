// src/structures/array.js

class ArrayStructure {
  constructor() {
    this.data = [];
  }

  insert(key, value) {
    this.data.push({key, value});
  }

  clear() {
    this.data = [];
  }

  get size() {
    return this.data.length;
  }
}

module.exports = ArrayStructure;
