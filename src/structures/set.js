class SetStructure {
  constructor() {
    this.data = new Set();
  }

  insert(key, value) {
    this.data.add({key, value});
  }

  clear() {
    this.data.clear();
  }

  get size() {
    return this.data.size;
  }
}

module.exports = SetStructure;