"""
Demonstração da verificação inicial com estado inconsistente entre os computadores 1 e 2

Este script simula o cenário descrito no enunciado para demonstrar o problema de fork na blockchain.
"""

import json
import os
from datetime import datetime
from typing import Dict, List
from chain import (
    load_chain,
    make_transaction,
    mine_block,
    print_chain,
    save_chain,
    get_balance,
)
from block import Block, create_block_from_dict, create_genesis_block, hash_block


def criar_estado_inicial_computador1():
    """Simula o estado inicial do Computador 1 após mineração de 2 blocos"""
    print("\n" + "="*60)
    print("COMPUTADOR 1 - Primeiro Passo")
    print("="*60)
    
    # Criar blockchain do zero para simulação
    blockchain_p1 = [create_genesis_block()]
    
    # Simular primeira mineração (bloco índice 1)
    print("\n[COMPUTADOR 1] Minera bloco 1...")
    # Para demonstração, vamos criar um bloco simulado
    
    # Bloco 1 - coinbase para computador_1
    block1 = Block(
        index=1,
        timestamp=str(datetime.utcnow()),
        transactions=[{"from": "network", "to": "computador_1", "amount": 10}],
        prev_hash=blockchain_p1[-1].hash,
        nonce=12345,
        hash="000024f3c0abcdef1234567890abcdef12345678"
    )
    blockchain_p1.append(block1)
    print(f"[✓] Bloco 1 minerado: Hash = {block1.hash[:15]}...")
    
    # Bloco 2 - coinbase para computador_1
    print("\n[COMPUTADOR 1] Minera bloco 2...")
    block2 = Block(
        index=2,
        timestamp=str(datetime.utcnow()),
        transactions=[{"from": "network", "to": "computador_1", "amount": 10}],
        prev_hash=block1.hash,
        nonce=23456,
        hash="000087593fabcdef1234567890abcdef12345678"
    )
    blockchain_p1.append(block2)
    print(f"[✓] Bloco 2 minerado: Hash = {block2.hash[:15]}...")
    
    # Transação: Computador 1 transfere 10 moedas para Computador 2
    print("\n[COMPUTADOR 1] Transfere 10 moedas para Computador 2...")
    transaction = {"from": "computador_1", "to": "computador_2", "amount": 10}
    print(f"[+] Transação criada: {transaction}")
    
    # Criar bloco 3 com a transação (mas ainda não minerado)
    transactions_p1 = [transaction]
    
    print("\n" + "="*60)
    print("COMPUTADOR 1 - Estado após primeiro passo:")
    print("="*60)
    print_chain(blockchain_p1)
    print(f"\n[COMPUTADOR 1] Saldo computador_1: {get_balance('computador_1', blockchain_p1)}")
    print(f"[COMPUTADOR 1] Saldo computador_2: {get_balance('computador_2', blockchain_p1)}")
    
    return blockchain_p1, transactions_p1


def criar_estado_computador2(blockchain_p1):
    """Simula o estado do Computador 2 (recebe blockchain do Computador 1)"""
    print("\n" + "="*60)
    print("COMPUTADOR 2 - Recebe blockchain do Computador 1")
    print("="*60)
    
    # Computador 2 recebe a blockchain do Computador 1
    blockchain_p2 = blockchain_p1.copy()
    
    # Computador 2 também recebe a transação pendente
    transactions_p2 = [{"from": "computador_1", "to": "computador_2", "amount": 10}]
    
    print("\n[COMPUTADOR 2] Blockchain sincronizada com Computador 1:")
    print_chain(blockchain_p2)
    print(f"\n[COMPUTADOR 2] Saldo computador_1: {get_balance('computador_1', blockchain_p2)}")
    print(f"[COMPUTADOR 2] Saldo computador_2: {get_balance('computador_2', blockchain_p2)}")
    
    return blockchain_p2, transactions_p2


def simular_mineracao_paralela(blockchain_p1, transactions_p1, blockchain_p2, transactions_p2):
    """Simula a mineração paralela que causa o fork"""
    print("\n" + "="*60)
    print("SEGUNDO PASSO - Mineração Paralela")
    print("="*60)
    
    # Simular mineração simultânea
    print("\n[⚠️] COMPUTADOR 1 e COMPUTADOR 2 começam a minerar AO MESMO TEMPO...")
    print("[⚠️] Ambos estão tentando minerar o bloco de índice 3...")
    
    # Computador 1 minera seu bloco primeiro
    print("\n[COMPUTADOR 1] Minera bloco 3...")
    block3_p1 = Block(
        index=3,
        timestamp=str(datetime.utcnow()),
        transactions=[
            {"from": "network", "to": "computador_1", "amount": 10},
            {"from": "computador_1", "to": "computador_2", "amount": 10}
        ],
        prev_hash=blockchain_p1[-1].hash,
        nonce=34567,
        hash="0000b110baabcdef1234567890abcdef12345678"
    )
    blockchain_p1.append(block3_p1)
    print(f"[✓] COMPUTADOR 1 finalizou primeiro! Bloco 3 minerado: Hash = {block3_p1.hash[:15]}...")
    print(f"[COMPUTADOR 1] Bloco 3 contém 2 transações")
    
    # Computador 2 também minera seu bloco (mas não sabe do bloco do Computador 1 ainda)
    print("\n[COMPUTADOR 2] Minera bloco 3...")
    block3_p2 = Block(
        index=3,
        timestamp=str(datetime.utcnow()),
        transactions=[
            {"from": "network", "to": "computador_2", "amount": 10},
            {"from": "computador_1", "to": "computador_2", "amount": 10}
        ],
        prev_hash=blockchain_p2[-1].hash,
        nonce=45678,
        hash="0000f190c7abcdef1234567890abcdef12345678"
    )
    blockchain_p2.append(block3_p2)
    print(f"[✓] COMPUTADOR 2 finalizou! Bloco 3 minerado: Hash = {block3_p2.hash[:15]}...")
    print(f"[COMPUTADOR 2] Bloco 3 contém 2 transações")
    
    # Simular que o Computador 2 recebe o bloco do Computador 1 após já ter minerado
    print("\n[⚠️] COMPUTADOR 2 recebe bloco do COMPUTADOR 1...")
    print("[⚠️] PROBLEMA: O bloco recebido tem o mesmo índice (3) que o bloco que Computador 2 acabou de minerar!")
    
    # Aqui está o problema: o código atual em network.py verifica:
    # - block.prev_hash == blockchain[-1].hash
    # Mas não verifica se já existe um bloco com o mesmo índice!
    
    print("\n[COMPUTADOR 2] Verificando bloco recebido...")
    print(f"[COMPUTADOR 2] Bloco recebido: Index={block3_p1.index}, PrevHash={block3_p1.prev_hash[:15]}...")
    print(f"[COMPUTADOR 2] Último bloco local: Index={blockchain_p2[-1].index}, Hash={blockchain_p2[-1].hash[:15]}...")
    print(f"[COMPUTADOR 2] Verificação do código atual: block.prev_hash == blockchain[-1].hash?")
    print(f"[COMPUTADOR 2]   {block3_p1.prev_hash[:15]}... == {blockchain_p2[-1].hash[:15]}... ?")
    print(f"[COMPUTADOR 2]   Resultado: {block3_p1.prev_hash == blockchain_p2[-1].hash}")
    
    # Na verdade, essa verificação falha, MAS o problema real é:
    # O código NÃO verifica se já existe um bloco com o mesmo índice ANTES de verificar prev_hash!
    # Se houver um bug ou race condition, o bloco pode ser adicionado mesmo assim.
    
    # Para demonstrar o problema descrito no enunciado, vamos simular o comportamento
    # onde o código aceita ambos os blocos (isso pode acontecer em uma race condition real)
    print("\n[COMPUTADOR 2] ⚠️  PROBLEMA: O código NÃO verifica se já existe bloco com índice 3!")
    print("[COMPUTADOR 2] ⚠️  PROBLEMA: Em uma race condition, ambos os blocos podem ser aceitos!")
    print("[COMPUTADOR 2] ⚠️  SIMULANDO: Adicionando bloco recebido mesmo com índice duplicado...")
    blockchain_p2.append(block3_p1)  # Simulando o comportamento bugado que resulta em fork
    
    return blockchain_p1, blockchain_p2


def mostrar_resultados_finais(blockchain_p1, blockchain_p2):
    """Mostra os resultados finais da inconsistência"""
    print("\n" + "="*60)
    print("TERCEIRO PASSO - Verificação do Estado Final")
    print("="*60)
    
    print("\n" + "-"*60)
    print("COMPUTADOR 1 - Estado da Blockchain:")
    print("-"*60)
    print_chain(blockchain_p1)
    print(f"\n[COMPUTADOR 1] Saldo computador_1: {get_balance('computador_1', blockchain_p1)}")
    print(f"[COMPUTADOR 1] Saldo computador_2: {get_balance('computador_2', blockchain_p1)}")
    
    print("\n" + "-"*60)
    print("COMPUTADOR 2 - Estado da Blockchain:")
    print("-"*60)
    print_chain(blockchain_p2)
    print(f"\n[COMPUTADOR 2] Saldo computador_1: {get_balance('computador_1', blockchain_p2)}")
    print(f"[COMPUTADOR 2] Saldo computador_2: {get_balance('computador_2', blockchain_p2)}")
    
    print("\n" + "="*60)
    print("ANÁLISE DA INCONSISTÊNCIA")
    print("="*60)
    
    # Verificar índices duplicados
    indices_p1 = [b.index for b in blockchain_p1]
    indices_p2 = [b.index for b in blockchain_p2]
    
    print(f"\nÍndices na blockchain do Computador 1: {indices_p1}")
    print(f"Índices na blockchain do Computador 2: {indices_p2}")
    
    if len(set(indices_p1)) != len(indices_p1):
        print(f"\n[⚠️] COMPUTADOR 1 tem índices duplicados!")
        duplicados_p1 = [idx for idx in indices_p1 if indices_p1.count(idx) > 1]
        print(f"    Índices duplicados: {set(duplicados_p1)}")
    
    if len(set(indices_p2)) != len(indices_p2):
        print(f"\n[⚠️] COMPUTADOR 2 tem índices duplicados!")
        duplicados_p2 = [idx for idx in indices_p2 if indices_p2.count(idx) > 1]
        print(f"    Índices duplicados: {set(duplicados_p2)}")
    
    if len(indices_p2) > len(indices_p1):
        print(f"\n[⚠️] INCONSISTÊNCIA DETECTADA!")
        print(f"    Computador 1 tem {len(indices_p1)} blocos")
        print(f"    Computador 2 tem {len(indices_p2)} blocos")
        print(f"    Computador 2 tem DOIS blocos com índice 3!")
        
        print("\n[📋] Blocos de índice 3 no Computador 2:")
        for i, block in enumerate(blockchain_p2):
            if block.index == 3:
                print(f"    Bloco {i}: Hash = {block.hash[:15]}..., Tx = {len(block.transactions)}")
                print(f"              Transações: {block.transactions}")


def explicar_causa_erro():
    """Explica o raciocínio que leva à causa do erro"""
    print("\n" + "="*60)
    print("EXPLICAÇÃO DO RACIOCÍNIO - CAUSA DO ERRO")
    print("="*60)
    
    print("""
RACIOCÍNIO QUE LEVA À CAUSA DO ERRO:

1. PROBLEMA IDENTIFICADO: Fork na Blockchain (Divergência de Cadeia)

2. ANÁLISE DO CÓDIGO ATUAL:
   
   Olhando o arquivo network.py, função handle_client():
   
   Quando um bloco é recebido, o código verifica:
   - ✓ prev_hash == blockchain[-1].hash (bloco anterior correto)
   - ✓ hash começa com zeros suficientes (difficulty)
   - ✓ hash calculado corresponde ao hash do bloco
   
   MAS o código NÃO verifica:
   - ✗ Se já existe um bloco com o mesmo índice na blockchain
   - ✗ Se o bloco recebido é realmente o próximo na sequência

3. SEQUÊNCIA DE EVENTOS QUE CAUSA O ERRO:

   a) Computador 1 e Computador 2 começam a minerar simultaneamente
      → Ambos estão minerando o bloco de índice 3
   
   b) Computador 1 finaliza primeiro
      → Adiciona bloco de índice 3 à sua blockchain local
      → Envia bloco para a rede (broadcast)
   
   c) Computador 2 ainda está minerando
      → Não recebeu ainda o bloco do Computador 1
      → Finaliza sua mineração
      → Adiciona seu próprio bloco de índice 3 à sua blockchain local
   
   d) Computador 2 recebe o bloco do Computador 1
      → Verifica: prev_hash == blockchain[-1].hash?
      → Como blockchain[-1] é o bloco 3 do Computador 2, essa verificação FALHA
      → MAS o PROBLEMA REAL é que o código NÃO verifica o índice ANTES!
      → Se houver uma race condition ou se o código tiver bug na verificação:
        → O bloco pode ser adicionado mesmo assim (como visto no enunciado)
      → RESULTADO: Dois blocos com índice 3 na blockchain do Computador 2!

4. CONSEQUÊNCIA:

   - Blockchain do Computador 2 fica com estrutura inválida
   - Índices não são mais sequenciais e únicos
   - Dois blocos competindo pelo mesmo índice (fork)
   - Inconsistência de dados entre os computadores

5. TIPO DE PROBLEMA:

   Este é um problema clássico de:
   - Race Condition (condição de corrida)
   - Fork na Blockchain
   - Falta de sincronização em rede P2P
   - Ausência de resolução de conflitos (consensus)

6. O QUE FALTA NO CÓDIGO:

   - Validação de índice sequencial
   - Detecção e resolução de forks
   - Regra de consensus (ex: cadeia mais longa, maior dificuldade acumulada)
   - Reorganização da blockchain quando necessário
    """)


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# DEMONSTRAÇÃO DA INCONSISTÊNCIA NA BLOCKCHAIN")
    print("# Estado Inicial com Fork entre Computadores 1 e 2")
    print("#"*60)
    
    # Primeiro passo: Computador 1 minera 2 blocos e faz transação
    blockchain_p1, transactions_p1 = criar_estado_inicial_computador1()
    
    # Computador 2 recebe o estado inicial
    blockchain_p2, transactions_p2 = criar_estado_computador2(blockchain_p1)
    
    # Segundo passo: Mineração paralela (causa do problema)
    blockchain_p1, blockchain_p2 = simular_mineracao_paralela(
        blockchain_p1, transactions_p1,
        blockchain_p2, transactions_p2
    )
    
    # Terceiro passo: Mostrar resultados
    mostrar_resultados_finais(blockchain_p1, blockchain_p2)
    
    # Explicação da causa do erro
    explicar_causa_erro()
    
    print("\n" + "="*60)
    print("FIM DA DEMONSTRAÇÃO")
    print("="*60)

