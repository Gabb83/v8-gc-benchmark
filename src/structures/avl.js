class No {
  constructor(key, value) { 
    this.key = key;
    this.value = value; 
    this.esquerda = null;
    this.direita = null; 
    this.altura = 1;
  }
}

class AVLStructure {
  constructor() {
    this.raiz = null;
    this._size = 0;
  }

  getAltura(no) {
    return no ? no.altura : 0;
  }

  getFatorBalanceamento(no) {
    return no ? this.getAltura(no.esquerda) - this.getAltura(no.direita) : 0;
  }

  atualizarAltura(no) {
    no.altura = 1 + Math.max(this.getAltura(no.esquerda), this.getAltura(no.direita));
  }

  rotacaoDireita(y) {
    const x = y.esquerda;
    const T2 = x ? x.direita : null;

    if (!x) return y;

    x.direita = y;
    y.esquerda = T2;

    this.atualizarAltura(y);
    this.atualizarAltura(x);

    return x;
  }

  rotacaoEsquerda(x) {
    const y = x.direita;
    const T2 = y ? y.esquerda : null;

    if (!y) return x;

    y.esquerda = x;
    x.direita = T2;

    this.atualizarAltura(x);
    this.atualizarAltura(y);

    return y;
  }

  insert(key, value) {
    this.raiz = this._insertNo(this.raiz, key, value);
  }

  _insertNo(no, key, value) {
    if (!no) {
      this._size++;
      return new No(key, value);
    }

    if(key < no.key) {
      no.esquerda = this._insertNo(no.esquerda, key, value);
    } else if(key > no.key) {
      no.direita = this._insertNo(no.direita, key, value);
    } else {
      no.value = value;
      return no;
    }

    this.atualizarAltura(no);
    const balanceamento = this.getFatorBalanceamento(no);

    if (balanceamento > 1 && no.esquerda && key < no.esquerda.key) {
      return this.rotacaoDireita(no);
    }

    if (balanceamento < -1 && no.direita && key > no.direita.key) {
      return this.rotacaoEsquerda(no);
    }

    if(balanceamento > 1 && no.esquerda && key > no.esquerda.key) {
      no.esquerda = this.rotacaoEsquerda(no.esquerda);
      return this.rotacaoDireita(no);
    }

    if(balanceamento < -1 && no.direita && key < no.direita.key) {
      no.direita = this.rotacaoDireita(no.direita);
      return this.rotacaoEsquerda(no);
    }

    return no;
  }

  clear() {
    this.raiz = null;
    this._size = 0;
  }

  get size() {
    return this._size;
  }
}

module.exports = AVLStructure;