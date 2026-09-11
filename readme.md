# ⚙️ V8-GC-Benchmark
É uma aplicação que mede o impacto das estruturas de dados em desempenho, comportamento e eficiência no Garbage Collector (GC) na Engine V8 do Node.js. O objetivo é fornecer insights sobre como diferentes estruturas de dados podem afetar a coleta de lixo e o desempenho geral da aplicação. Usado em Pesquisa e Desenvolvimento (P&D) para otimização de aplicações Node.js.

It is an aplication that measures the impact of data structures on performance, behavior, and efficiency in the Garbage Collector (GC) in the V8 Engine of Node.js. The goal is to provide insights into how different data structures can affect garbage collection and overall application performance. Used in Research and Development (R&D) for optimizing Node.js applications.

## Estruturas de Dados Testadas
- As estruturas de dados testadas incluem:
  - Estruturas Nativas da V8 (Structures of V8 Engine):
    - Map, Set, Array.
  - Estruturas de Dados Personalizadas em JavaScript (Custom Data Structures in JavaScript):
    - Árvvores: 
      - Árvore Binária de Busca (Binary Search Tree) e Árvore AVL (AVL Tree).

## Métricas Coletadas
- As métricas coletadas durante os testes incluem:
  - Análise de memória: Heap Used, Heap Peak e RSS memory.
  - Análise do Garbage Collector: Tempo de pausa, número de minor e major GC, taxa de promoção.
  - Tempo de resposta por latência média (ms). 