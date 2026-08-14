class No {
  contrcutor(key, value) {
    this.key = key
    this.value = value; 
    this.esquerda = null;
    this.direita = null; 
    this.altura = 1;
  }
}

class AVLStructure {
  contrcutor() {
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

  rotaçãoDir(y) {
    const x = y.esquerda;
    const T2 = x.direita;

    x.direita = y;
    y.esquerda = T2;

    this.atualizarAltura(y);
    this.atualizarAltura(x);

    return x;
  }

  rotateEsq(x) {
    const y = x.direita;
    const T2 = y.esquerda;

    y.esquerda = x;
    x.direita = T2;

    this.atualizarAltura(x);
    this.atualizarAltura(y);

    return y;
  }

  insert(key, value) {
    this.raiz = this._insertNo(this.raiz, key, value);
    this._size++;
  }

  _insertNo(no, key, value) {
    if(!no) {
      return new No(key, value);
    }

    if(key < no.key) {
      no.left = this._insertNo(no.esquerda, key, value);
    } else if (key > no.key) {
      no.direita = this._insertNo(no.direita, key, value);
    } else {
      no.value = value;
      return no;
    }

    this.atualizarAltura(no);
    const balanceamento = this.getFatorBalanceamento(no);

    if (balanceamento > 1 && key < no.esquerda.key) {
      return this.rotateDir(no);
    }

    if (balanceamento < -1 && key > no.direita.key) {
      return this.rotateEsq(no);
    }

    if (balanceamento > 1 && key > no.esquerda.key) {
      no.esquerda = this.rotateEsq(no.esquerda);
      return this.rotateDir(no);
    }

    if (balanceamento < -1 && key < no.direita.key) {
      no.direita = this.rotateDir(no.direita);
      return this.rotateEsq(no);
    }

    return no;
  }

  clear() {
    this.raiz = null;
    this._size = 0;
  }

  _size() {
    return this._size;
  }
}

module.exports = AVLStructure;