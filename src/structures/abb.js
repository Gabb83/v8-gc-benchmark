// src/structures/abb.js

class No {
  constructor(key, value) {
    this.key = key
    this.value = value; 
    this.esquerda = null;
    this.direita = null; 
  }
}

class ABBStructure {
  constructor() {
    this.raiz = null;
    this._size = 0;
  }

  insert(key, value) {
    const novoNo = new No(key, value);
    if (this.raiz === null) {
      this.raiz = novoNo;
    } else {
      this._insertNo(this.raiz, novoNo);
    }
    this._size++;
  }

  _insertNo(no, novoNo) {
    if (novoNo.key < no.key) {
      if (no.esquerda === null) {
        no.esquerda = novoNo;
      } else {
        this._insertNo(no.esquerda, novoNo);
      }
    } else {
      if (no.direita === null) {
        no.direita = novoNo;
      } else {
        this._insertNo(no.direita, novoNo);
      }
    }
  }

  clear() {
    this.raiz = null;
    this._size = 0;
  }

  get size() {
    return this._size;
  }
}

module.exports = ABBStructure;