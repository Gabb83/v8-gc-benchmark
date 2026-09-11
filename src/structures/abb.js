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

  getAltura() {
    if (this.raiz === null) return -1;

    let altura = -1;
    const fila = [this.raiz];

    while (fila.length > 0) {
      const tamanhoNivel = fila.length;
      altura++;

      for (let i = 0; i < tamanhoNivel; i++) {
        const noAtual = fila.shift();
        if (noAtual.esquerda) fila.push(noAtual.esquerda);
        if (noAtual.direita) fila.push(noAtual.direita);
      }
    }

    return altura;
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