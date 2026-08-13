//src/structures/set.js

class SetStructure {
  constructor() {
    this.data = new Set();
  }

  insert(value) {
    this.data.add(value);
  }

  clear() {
    this.data.clear();
  }

  get size() {
    return this.data.size;
  }
}

module.exports = SetStructure;