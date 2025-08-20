from collections import deque 
from dataclasses import dataclass
import time
from typing import Dict, Deque, List, Optional
import os

@dataclass
class Produto:
    id: int
    nome: str
    quantidade: int
    preco: float

    def __str__(self) -> str:
        return f"ID: {self.id} | Nome: {self.nome} | Quantidade: {self.quantidade} | Preço: R${self.preco:.2f}"


@dataclass
class Cliente:
    id: int
    nome: str
    gastos: float = 0.0

    def __str__(self) -> str:
        return f"ID Cliente: {self.id} | Nome: {self.nome} | Total Gasto: R${self.gastos:.2f}"


@dataclass
class Venda:
    id: int
    produto_id: int
    cliente_id: int
    quantidade: int
    valor: float
    produto_nome: str
    cliente_nome: str


class Estoque:
    def __init__(self):
        self.produtos: Dict[int, Produto] = {}
        self.clientes: Dict[int, Cliente] = {}
        self.fila_vendas: Deque[Venda] = deque()
        self.pilha_operacoes: List[Venda] = []
        self.valor_total_vendas: float = 0.0
        self._prox_id_produto = 1
        self._prox_id_cliente = 1
        self._prox_id_venda = 1
        self._espera_segundos = 5
        self.arquivo = "estoque.txt"

    def aguardar(self, msg: Optional[str] = None, segundos: Optional[int] = None):
        if msg:
            print(msg)
        s = self._espera_segundos if segundos is None else segundos
        print(f"(aguardando {s} segundos...)")
        time.sleep(s)
    
    def salvar_em_arquivo(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            f.write("==== PRODUTOS ====\n")
            for p in self.produtos.values():
                f.write(str(p) + "\n")

            f.write("\n==== CLIENTES ====\n")
            for c in self.clientes.values():
                f.write(str(c) + "\n")

            f.write("\n==== VENDAS ====\n")
            for v in self.pilha_operacoes:
                f.write(
                    f"Venda {v.id} | Produto: {v.produto_nome} (ID {v.produto_id}) | "
                    f"Cliente: {v.cliente_nome} (ID {v.cliente_id}) | "
                    f"Qtd: {v.quantidade} | Valor: R${v.valor:.2f}\n"
                )

            total_estoque = self._calc_valor_total_estoque()
            f.write(f"\nValor total do estoque: R${total_estoque:.2f}\n")
            f.write(f"Valor total de vendas: R${self.valor_total_vendas:.2f}\n")

        self.aguardar(f"Arquivo '{self.arquivo}' gerado/atualizado com sucesso!")

    def _obter_produto(self, id_produto: int) -> Optional[Produto]:
        return self.produtos.get(id_produto)

    def _obter_cliente(self, id_cliente: int) -> Optional[Cliente]:
        return self.clientes.get(id_cliente)

    def _calc_valor_total_estoque(self) -> float:
        return sum(p.quantidade * p.preco for p in self.produtos.values())
    
    def cadastrar_produto(self, nome: str, quantidade: int, preco: float):
        if not nome.strip():
            self.aguardar("Nome do produto não pode ser vazio.")
            return
        if quantidade <= 0:
            self.aguardar("Quantidade deve ser maior que zero.")
            return
        if preco <= 0:
            self.aguardar("Preço deve ser maior que zero.")
            return

        pid = self._prox_id_produto
        self._prox_id_produto += 1

        novo = Produto(pid, nome.strip(), quantidade, preco)
        self.produtos[pid] = novo

        print("Produto cadastrado com sucesso!")
        print(novo)
        self.aguardar()

    def listar_produtos(self):
        if not self.produtos:
            self.aguardar("Estoque vazio!")
            return
        print("\n--- Lista de Produtos ---")
        for p in self.produtos.values():
            print(p)
        self.aguardar()

    def buscar_produto_por_id(self, id_produto: int):
        produto = self._obter_produto(id_produto)
        if produto:
            print("\n--- Produto Encontrado ---")
            print(produto)
        else:
            print(f"Nenhum produto encontrado com o ID {id_produto}.")
        self.aguardar()

    def cadastrar_cliente(self, nome: str):
        if not nome.strip():
            self.aguardar("Nome do cliente não pode ser vazio.")
            return

        cid = self._prox_id_cliente
        self._prox_id_cliente += 1

        novo = Cliente(cid, nome.strip())
        self.clientes[cid] = novo

        print("Cliente cadastrado com sucesso!")
        print(novo)
        self.aguardar()

    def listar_clientes(self):
        if not self.clientes:
            self.aguardar("Nenhum cliente cadastrado.")
            return
        print("\n--- Lista de Clientes ---")
        for c in self.clientes.values():
            print(c)
        self.aguardar()

    def realizar_venda(self, id_produto: int, quantidade: int, id_cliente: int):
        produto = self._obter_produto(id_produto)
        if not produto:
            self.aguardar("Produto não encontrado!")
            return

        cliente = self._obter_cliente(id_cliente)
        if not cliente:
            self.aguardar("Cliente não encontrado!")
            return

        if quantidade <= 0:
            self.aguardar("Quantidade deve ser maior que zero.")
            return

        if quantidade > produto.quantidade:
            self.aguardar("Quantidade indisponível no estoque!")
            return
        
        produto.quantidade -= quantidade
        valor = quantidade * produto.preco
        cliente.gastos += valor
        self.valor_total_vendas += valor

        vid = self._prox_id_venda
        self._prox_id_venda += 1

        venda = Venda(
            id=vid,
            produto_id=produto.id,
            cliente_id=cliente.id,
            quantidade=quantidade,
            valor=valor,
            produto_nome=produto.nome,
            cliente_nome=cliente.nome,
        )

        self.fila_vendas.append(venda)
        self.pilha_operacoes.append(venda)

        print(f"Venda realizada com sucesso! (ID Venda {venda.id}) Valor: R${valor:.2f}")
        self.aguardar()

    def visualizar_fila(self):
        if not self.fila_vendas:
            self.aguardar("Fila de vendas vazia.")
            return

        print("\n--- Fila de Vendas (FIFO) ---")
        for v in list(self.fila_vendas):
            print(
                f"Venda {v.id} | Produto: {v.produto_nome} (ID {v.produto_id}) | "
                f"Cliente: {v.cliente_nome} (ID {v.cliente_id}) | "
                f"Qtd: {v.quantidade} | Valor: R${v.valor:.2f}"
            )
        self.aguardar()

    def atender_proxima_venda(self):
        if not self.fila_vendas:
            self.aguardar("Não há vendas na fila.")
            return

        venda = self.fila_vendas.popleft()
        print(
            f"Atendida a venda {venda.id} - "
            f"{venda.quantidade}x {venda.produto_nome} para {venda.cliente_nome} "
            f"(R${venda.valor:.2f})."
        )
        self.aguardar()

    def desfazer_ultima_operacao(self):
        if not self.pilha_operacoes:
            self.aguardar("Nenhuma operação para desfazer.")
            return

        venda = self.pilha_operacoes.pop()

        produto = self._obter_produto(venda.produto_id)
        cliente = self._obter_cliente(venda.cliente_id)

        if produto:
            produto.quantidade += venda.quantidade
        if cliente:
            cliente.gastos -= venda.valor
            if cliente.gastos < 0:
                cliente.gastos = 0.0

        self.valor_total_vendas -= venda.valor
        if self.valor_total_vendas < 0:
            self.valor_total_vendas = 0.0

        try:
            for item in self.fila_vendas:
                if item.id == venda.id:
                    self.fila_vendas.remove(item)
                    break
        except ValueError:
            pass

        self.aguardar("Última operação desfeita com sucesso!")

    def exibir_valor_total_estoque(self):
        total = self._calc_valor_total_estoque()
        print(f"Valor total do estoque: R${total:.2f}")
        self.aguardar()

    def exibir_valor_total_vendas(self):
        print(f"Valor total de vendas realizadas: R${self.valor_total_vendas:.2f}")
        self.aguardar()

    def exibir_clientes_valores(self):
        if not self.clientes:
            self.aguardar("Nenhum cliente encontrado.")
            return

        print("\n--- Clientes e Valores Gastos ---")
        for c in self.clientes.values():
            print(c)
        self.aguardar()


def menu():
    estoque = Estoque()

    while True:
        print("\n===== MENU ESTOQUE =====")
        print("0  - Gerar arquivo TXT") 
        print("1  - Cadastrar cliente")
        print("2  - Listar clientes")
        print("3  - Cadastrar produto")
        print("4  - Listar produtos")
        print("5  - Realizar venda")
        print("6  - Visualizar fila de vendas")
        print("7  - Atender PRÓXIMA venda (FIFO)")
        print("8  - Desfazer última operação")
        print("9  - Exibir valor total do estoque")
        print("10 - Exibir valor total de vendas realizadas")
        print("11 - Exibir clientes e valores gastos")
        print("12 - Buscar produto por ID")  
        print("13 - Sair")

        escolha = input("Escolha: ").strip()

        try:
            if escolha == "0":
                estoque.salvar_em_arquivo()

            elif escolha == "1":
                nome = input("Digite o nome do cliente: ")
                estoque.cadastrar_cliente(nome)

            elif escolha == "2":
                estoque.listar_clientes()

            elif escolha == "3":
                nome = input("Digite o nome do produto: ")
                qtd = int(input("Digite a quantidade: "))
                preco = float(input("Digite o preço: "))
                estoque.cadastrar_produto(nome, qtd, preco)

            elif escolha == "4":
                estoque.listar_produtos()

            elif escolha == "5":
                id_produto = int(input("Digite o ID do produto: "))
                qtd = int(input("Digite a quantidade: "))
                id_cliente = int(input("Digite o ID do cliente: "))
                estoque.realizar_venda(id_produto, qtd, id_cliente)

            elif escolha == "6":
                estoque.visualizar_fila()

            elif escolha == "7":
                estoque.atender_proxima_venda()

            elif escolha == "8":
                estoque.desfazer_ultima_operacao()

            elif escolha == "9":
                estoque.exibir_valor_total_estoque()

            elif escolha == "10":
                estoque.exibir_valor_total_vendas()

            elif escolha == "11":
                estoque.exibir_clientes_valores()

            elif escolha == "12":
                id_prod = int(input("Digite o ID do produto: "))
                estoque.buscar_produto_por_id(id_prod)

            elif escolha == "13":
                print("Saindo do sistema... Até logo!")
                break

            else:
                print("Opção inválida!")
                time.sleep(3)

        except ValueError:
            print("Entrada inválida. Digite números onde solicitado.")
            time.sleep(5)
        except Exception as e:
            print("Erro inesperado:", e)
            print("O programa continua rodando!")
            time.sleep(5)


if __name__ == "__main__":
    menu()
