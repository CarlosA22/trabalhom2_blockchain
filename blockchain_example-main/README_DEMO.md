# Demonstração da Inconsistência na Blockchain

Este script demonstra o problema de fork/inconsistência na blockchain quando dois computadores mineram blocos simultaneamente.

## Como executar

```bash
python demo_inconsistencia.py
```

## O que o script faz

1. **Primeiro passo**: Simula o Computador 1 minerando 2 blocos em sequência e fazendo uma transação para o Computador 2
2. **Segundo passo**: Simula a mineração paralela de ambos os computadores (causando fork)
3. **Terceiro passo**: Mostra os resultados da inconsistência e explica a causa do erro

## Resultados esperados

O script mostrará:
- Estado da blockchain do Computador 1 (consistente)
- Estado da blockchain do Computador 2 (inconsistente - dois blocos com índice 3)
- Explicação detalhada do raciocínio que leva à causa do erro

## O problema

Quando dois computadores mineram blocos simultaneamente, ambos podem criar blocos com o mesmo índice. O código atual em `network.py` não verifica se já existe um bloco com o mesmo índice antes de adicionar um novo bloco à blockchain, resultando em um fork.

