class MapStructure {
  constructor() {
    this.data = new Map();
  }

  insert(key, value) {
    this.data.set(key, value);
  }

  clear() {
    this.data.clear();
  }

  get size() {
    return this.data.size;
  }
}

module.exports = MapStructure;