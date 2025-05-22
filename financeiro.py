# Importações necessárias
import flet as ft
import csv
from datetime import datetime
from collections import defaultdict
import os

# ================== CONFIGURAÇÕES ================== #
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
BACKGROUND_COLOR = "#f8f9fa"
CARD_COLOR = "#ffffff"
TEXT_COLOR = "#212121"
SUCCESS_COLOR = "#28a745"
ERROR_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"
BORDER_COLOR = "#dee2e6"
INVESTMENT_COLOR = "#6f42c1"
SEARCH_HIGHLIGHT_COLOR = "#ffeb3b"

# Categorias pré-definidas
CATEGORIAS = {
    "receita": ["Salário", "Freelance", "Investimentos", "Outros"],
    "despesa": ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Educação", "Outros"],
    "investimento": ["Ações", "Fundos", "Renda Fixa", "Criptomoedas", "Outros"]
}

# ================== MODELO ================== #
class Transacao:
    def __init__(self, descricao, valor, data, tipo, categoria):
        self.descricao = descricao
        self.valor = float(valor)
        self.data = data
        self.tipo = tipo
        self.categoria = categoria
        self.id = datetime.now().timestamp()

# ================== CONTROLE ================== #
class ControleFinanceiro:
    def __init__(self, page):
        self.page = page
        self.setup_page()
        self.transacoes = []
        self.filtro_ativo = "todos"
        self.termo_pesquisa = ""
        self.carregar_dados()
        self.criar_componentes()
        self.montar_layout()

    def setup_page(self):
        self.page.title = "Controle Financeiro Pessoal"
        self.page.window_width = 1200
        self.page.window_height = 850
        self.page.bgcolor = BACKGROUND_COLOR
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

    def mostrar_mensagem(self, mensagem, tipo="sucesso"):
        cores = {
            "sucesso": SUCCESS_COLOR,
            "erro": ERROR_COLOR,
            "aviso": WARNING_COLOR,
            "investimento": INVESTMENT_COLOR
        }
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem, color="white"),
            bgcolor=cores[tipo],
            behavior=ft.SnackBarBehavior.FLOATING
        )
        self.page.snack_bar.open = True
        self.page.update()

    def carregar_dados(self):
        try:
            if os.path.exists("financas.csv"):
                with open("financas.csv", mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        transacao = Transacao(
                            row['descricao'],
                            row['valor'],
                            row['data'],
                            row['tipo'],
                            row.get('categoria', 'Outros')
                        )
                        if 'id' in row:
                            transacao.id = float(row['id'])
                        self.transacoes.append(transacao)
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao carregar dados: {str(e)}", "erro")

    def salvar_dados(self):
        try:
            with open("financas.csv", mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['id', 'descricao', 'valor', 'data', 'tipo', 'categoria'])
                writer.writeheader()
                for transacao in self.transacoes:
                    writer.writerow({
                        'id': transacao.id,
                        'descricao': transacao.descricao,
                        'valor': transacao.valor,
                        'data': transacao.data,
                        'tipo': transacao.tipo,
                        'categoria': transacao.categoria
                    })
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao salvar dados: {str(e)}", "erro")

    def adicionar_transacao(self, e):
        descricao = self.input_descricao.value.strip()
        valor = self.input_valor.value.replace(",", ".").strip()
        data = self.input_data.value.strip() or datetime.now().strftime("%d/%m/%Y")
        tipo = self.select_tipo.value
        categoria = self.select_categoria.value

        if not descricao or not valor:
            self.mostrar_mensagem("Preencha todos os campos obrigatórios!", "aviso")
            return

        try:
            valor_float = float(valor)
            if valor_float <= 0:
                self.mostrar_mensagem("O valor deve ser positivo!", "aviso")
                return

            datetime.strptime(data, "%d/%m/%Y")

            nova_transacao = Transacao(descricao, valor_float, data, tipo, categoria)
            self.transacoes.append(nova_transacao)
            self.salvar_dados()
            
            self.input_descricao.value = ""
            self.input_valor.value = ""
            self.atualizar_interface()
            
            tipo_mensagem = "sucesso" if tipo == "receita" else "erro" if tipo == "despesa" else "investimento"
            self.mostrar_mensagem(f"Transação ({tipo}) adicionada com sucesso!", tipo_mensagem)
            
        except ValueError as ve:
            if "time data" in str(ve):
                self.mostrar_mensagem("Formato de data inválido! Use dd/mm/aaaa", "aviso")
            else:
                self.mostrar_mensagem("Valor inválido! Use números.", "aviso")
        except Exception as ex:
            self.mostrar_mensagem(f"Erro: {str(ex)}", "erro")

    def excluir_transacao(self, transacao_id):
        self.transacoes = [t for t in self.transacoes if t.id != transacao_id]
        self.salvar_dados()
        self.atualizar_interface()
        self.mostrar_mensagem("Transação excluída com sucesso!")

    def aplicar_filtro(self, tipo):
        self.filtro_ativo = tipo
        self.atualizar_interface()

    def atualizar_categorias(self, e):
        tipo = self.select_tipo.value
        self.select_categoria.options = [
            ft.dropdown.Option(cat) for cat in CATEGORIAS.get(tipo, ["Outros"])
        ]
        self.select_categoria.value = CATEGORIAS.get(tipo, ["Outros"])[0]
        self.page.update()

    def pesquisar_transacoes(self, e):
        self.termo_pesquisa = self.input_pesquisa.value.lower().strip()
        self.atualizar_interface()

    def calcular_totais(self):
        receitas = sum(t.valor for t in self.transacoes if t.tipo == 'receita')
        despesas = sum(t.valor for t in self.transacoes if t.tipo == 'despesa')
        investimentos = sum(t.valor for t in self.transacoes if t.tipo == 'investimento')
        
        # Calcula saldo considerando receitas menos despesas e investimentos
        saldo = receitas - despesas - investimentos
        
        return {
            'receitas': receitas,
            'despesas': despesas,
            'investimentos': investimentos,
            'saldo': saldo
        }

    def calcular_lucros_por_periodo(self):
        lucro_mensal = defaultdict(float)
        lucro_anual = defaultdict(float)
        
        for transacao in self.transacoes:
            try:
                if transacao.tipo == 'despesa':
                    sinal = -1
                elif transacao.tipo == 'investimento':
                    sinal = -1  # Investimentos reduzem o lucro
                else:
                    sinal = 1
                
                data = datetime.strptime(transacao.data, "%d/%m/%Y")
                mes_ano = data.strftime("%m/%Y")
                ano = data.strftime("%Y")
                
                lucro_mensal[mes_ano] += transacao.valor * sinal
                lucro_anual[ano] += transacao.valor * sinal
            except:
                continue
        
        return lucro_mensal, lucro_anual

    def criar_componentes(self):
        # Campos de entrada
        self.input_descricao = ft.TextField(
            label="Descrição", 
            expand=True, 
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )

        self.input_valor = ft.TextField(
            label="Valor (R$)", 
            prefix_text="R$ ", 
            width=200,
            keyboard_type=ft.KeyboardType.NUMBER, 
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )

        self.input_data = ft.TextField(
            label="Data (dd/mm/aaaa)", 
            width=200,
            value=datetime.now().strftime("%d/%m/%Y"), 
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )

        self.select_tipo = ft.Dropdown(
            label="Tipo", 
            width=200, 
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR,
            options=[
                ft.dropdown.Option("receita", "Receita"),
                ft.dropdown.Option("despesa", "Despesa"),
                ft.dropdown.Option("investimento", "Investimento"),
            ],
            value="receita",
            on_change=self.atualizar_categorias
        )

        self.select_categoria = ft.Dropdown(
            label="Categoria", 
            width=200, 
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR,
            options=[ft.dropdown.Option(cat) for cat in CATEGORIAS["receita"]],
            value=CATEGORIAS["receita"][0]
        )

        self.input_pesquisa = ft.TextField(
            label="Pesquisar transações",
            prefix_icon="search",
            on_change=self.pesquisar_transacoes,
            expand=True,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )

        self.btn_adicionar = ft.ElevatedButton(
            "Adicionar", 
            icon="add", 
            on_click=self.adicionar_transacao,
            bgcolor=PRIMARY_COLOR, 
            color="white", 
            height=45
        )

        self.btn_limpar = ft.TextButton(
            "Limpar Campos", 
            icon="clear", 
            on_click=self.limpar_campos,
            style=ft.ButtonStyle(color=SECONDARY_COLOR)
        )

        # Filtros
        self.btn_filtro_todos = ft.ElevatedButton(
            "Todos", 
            on_click=lambda e: self.aplicar_filtro("todos"),
            bgcolor=PRIMARY_COLOR if self.filtro_ativo == "todos" else BACKGROUND_COLOR,
            color="white" if self.filtro_ativo == "todos" else PRIMARY_COLOR
        )

        self.btn_filtro_receitas = ft.ElevatedButton(
            "Receitas", 
            on_click=lambda e: self.aplicar_filtro("receita"),
            bgcolor=PRIMARY_COLOR if self.filtro_ativo == "receita" else BACKGROUND_COLOR,
            color="white" if self.filtro_ativo == "receita" else SUCCESS_COLOR
        )

        self.btn_filtro_despesas = ft.ElevatedButton(
            "Despesas", 
            on_click=lambda e: self.aplicar_filtro("despesa"),
            bgcolor=PRIMARY_COLOR if self.filtro_ativo == "despesa" else BACKGROUND_COLOR,
            color="white" if self.filtro_ativo == "despesa" else ERROR_COLOR
        )

        self.btn_filtro_investimentos = ft.ElevatedButton(
            "Investimentos", 
            on_click=lambda e: self.aplicar_filtro("investimento"),
            bgcolor=PRIMARY_COLOR if self.filtro_ativo == "investimento" else BACKGROUND_COLOR,
            color="white" if self.filtro_ativo == "investimento" else INVESTMENT_COLOR
        )

        # Cards - Mantemos apenas 4 cards agora
        card_style = {
            "width": 220, 
            "height": 110, 
            "border_radius": 12,
            "padding": 15, 
            "bgcolor": CARD_COLOR
        }

        self.card_receitas = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("RECEITAS", size=12, weight="bold", color=TEXT_COLOR),
                    ft.Text("R$ 0.00", size=20, color=SUCCESS_COLOR, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ), elevation=3)

        self.card_despesas = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("DESPESAS", size=12, weight="bold", color=TEXT_COLOR),
                    ft.Text("R$ 0.00", size=20, color=ERROR_COLOR, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ), elevation=3)

        self.card_saldo = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("SALDO", size=12, weight="bold", color=TEXT_COLOR),
                    ft.Text("R$ 0.00", size=20, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ), elevation=3)

        self.card_investimentos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("INVESTIMENTOS", size=12, weight="bold", color=TEXT_COLOR),
                    ft.Text("R$ 0.00", size=20, color=INVESTMENT_COLOR, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ), elevation=3)

        # Tabela
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Descrição", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Valor", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Data", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Tipo", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Categoria", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Ações", weight="bold", color=TEXT_COLOR)),
            ],
            border=ft.border.all(1, BORDER_COLOR),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, BORDER_COLOR),
            horizontal_lines=ft.border.BorderSide(1, BORDER_COLOR),
        )

        # Relatórios
        self.relatorio_mensal = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Mês/Ano", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Lucro", weight="bold", color=TEXT_COLOR)),
            ],
            border=ft.border.all(1, BORDER_COLOR),
            border_radius=10
        )

        self.relatorio_anual = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ano", weight="bold", color=TEXT_COLOR)),
                ft.DataColumn(ft.Text("Lucro", weight="bold", color=TEXT_COLOR)),
            ],
            border=ft.border.all(1, BORDER_COLOR),
            border_radius=10
        )

    def criar_texto_com_destaque(self, texto, termo_pesquisa):
        if not termo_pesquisa or termo_pesquisa.lower() not in texto.lower():
            return ft.Text(texto, color=TEXT_COLOR)
        
        partes = []
        texto_lower = texto.lower()
        termo_lower = termo_pesquisa.lower()
        inicio = 0
        pos = texto_lower.find(termo_lower)
        
        while pos != -1:
            if inicio < pos:
                partes.append(ft.Text(texto[inicio:pos], color=TEXT_COLOR))
            
            partes.append(ft.Text(
                texto[pos:pos+len(termo_pesquisa)],
                weight="bold",
                bgcolor=SEARCH_HIGHLIGHT_COLOR,
                color=TEXT_COLOR
            ))
            
            inicio = pos + len(termo_pesquisa)
            pos = texto_lower.find(termo_lower, inicio)
        
        if inicio < len(texto):
            partes.append(ft.Text(texto[inicio:], color=TEXT_COLOR))
        
        return ft.Row(partes, wrap=True)

    def limpar_campos(self, e):
        self.input_descricao.value = ""
        self.input_valor.value = ""
        self.input_data.value = datetime.now().strftime("%d/%m/%Y")
        self.page.update()

    def criar_botao_excluir(self, transacao_id):
        return ft.IconButton(
            icon="delete", 
            icon_color=ERROR_COLOR,
            tooltip="Excluir", 
            on_click=lambda e: self.excluir_transacao(transacao_id)
        )

    def atualizar_interface(self):
        totais = self.calcular_totais()
        lucro_mensal, lucro_anual = self.calcular_lucros_por_periodo()
        
        # Atualiza cards com os novos valores
        self.card_receitas.content.content.controls[1].value = f"R$ {totais['receitas']:.2f}"
        self.card_despesas.content.content.controls[1].value = f"R$ {totais['despesas']:.2f}"
        self.card_saldo.content.content.controls[1].value = f"R$ {totais['saldo']:.2f}"
        self.card_saldo.content.content.controls[1].color = SUCCESS_COLOR if totais['saldo'] >= 0 else ERROR_COLOR
        self.card_investimentos.content.content.controls[1].value = f"R$ {totais['investimentos']:.2f}"
        
        transacoes_filtradas = self.transacoes
        if self.filtro_ativo != "todos":
            transacoes_filtradas = [t for t in self.transacoes if t.tipo == self.filtro_ativo]
        
        if self.termo_pesquisa:
            transacoes_filtradas = [t for t in transacoes_filtradas 
                                  if self.termo_pesquisa.lower() in t.descricao.lower()]
        
        linhas = []
        for transacao in sorted(transacoes_filtradas, 
                              key=lambda x: datetime.strptime(x.data, "%d/%m/%Y"), 
                              reverse=True):
            cor = {
                "receita": SUCCESS_COLOR,
                "despesa": ERROR_COLOR,
                "investimento": INVESTMENT_COLOR
            }.get(transacao.tipo, TEXT_COLOR)
            
            linhas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(self.criar_texto_com_destaque(transacao.descricao, self.termo_pesquisa)),
                        ft.DataCell(ft.Text(f"R$ {transacao.valor:.2f}", color=cor)),
                        ft.DataCell(ft.Text(transacao.data, color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(transacao.tipo.capitalize(), color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(transacao.categoria, color=TEXT_COLOR)),
                        ft.DataCell(self.criar_botao_excluir(transacao.id))
                    ]
                )
            )
        
        self.tabela.rows = linhas
        
        self.relatorio_mensal.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(mes_ano, color=TEXT_COLOR)),
                ft.DataCell(ft.Text(f"R$ {lucro:.2f}", 
                                  color=SUCCESS_COLOR if lucro >= 0 else ERROR_COLOR))
            ]) for mes_ano, lucro in sorted(lucro_mensal.items(), reverse=True)
        ]
        
        self.relatorio_anual.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(ano, color=TEXT_COLOR)),
                ft.DataCell(ft.Text(f"R$ {lucro:.2f}", 
                                  color=SUCCESS_COLOR if lucro >= 0 else ERROR_COLOR))
            ]) for ano, lucro in sorted(lucro_anual.items(), reverse=True)
        ]
        
        self.btn_filtro_todos.bgcolor = PRIMARY_COLOR if self.filtro_ativo == "todos" else BACKGROUND_COLOR
        self.btn_filtro_todos.color = "white" if self.filtro_ativo == "todos" else PRIMARY_COLOR
        
        self.btn_filtro_receitas.bgcolor = PRIMARY_COLOR if self.filtro_ativo == "receita" else BACKGROUND_COLOR
        self.btn_filtro_receitas.color = "white" if self.filtro_ativo == "receita" else SUCCESS_COLOR
        
        self.btn_filtro_despesas.bgcolor = PRIMARY_COLOR if self.filtro_ativo == "despesa" else BACKGROUND_COLOR
        self.btn_filtro_despesas.color = "white" if self.filtro_ativo == "despesa" else ERROR_COLOR
        
        self.btn_filtro_investimentos.bgcolor = PRIMARY_COLOR if self.filtro_ativo == "investimento" else BACKGROUND_COLOR
        self.btn_filtro_investimentos.color = "white" if self.filtro_ativo == "investimento" else INVESTMENT_COLOR
        
        self.page.update()

    def montar_layout(self):
        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("NOVA TRANSAÇÃO", size=18, weight="bold", color=TEXT_COLOR),
                    ft.Divider(height=10),
                    ft.Row([self.input_descricao, self.input_valor]),
                    ft.Row([self.input_data, self.select_tipo, self.select_categoria]),
                    ft.Row([self.btn_limpar, self.btn_adicionar], alignment="end")
                ], spacing=10),
                padding=20,
                bgcolor=CARD_COLOR
            ),
            elevation=3,
            margin=ft.margin.only(bottom=20)
        )
        filtros = ft.Row(
            [self.btn_filtro_todos, self.btn_filtro_receitas, 
             self.btn_filtro_despesas, self.btn_filtro_investimentos],
            spacing=10
        )
        
        pesquisa = ft.Row(
            [self.input_pesquisa],
            spacing=20,
            alignment="spaceBetween"
        )
        
        # Cards centralizados
        totais = ft.Row(
            [
                ft.Column(
                    [self.card_receitas],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Column(
                    [self.card_despesas],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Column(
                    [self.card_saldo],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Column(
                    [self.card_investimentos],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )
        
        relatorios = ft.Row([
            ft.Column([
                ft.Text("LUCRO MENSAL", size=16, weight="bold", color=TEXT_COLOR),
                ft.Container(
                    content=ft.ListView([self.relatorio_mensal], height=200),
                    border=ft.border.all(1, BORDER_COLOR),
                    border_radius=10,
                    padding=10,
                    bgcolor=CARD_COLOR
                )
            ], expand=True),
            
            ft.Column([
                ft.Text("LUCRO ANUAL", size=16, weight="bold", color=TEXT_COLOR),
                ft.Container(
                    content=ft.ListView([self.relatorio_anual], height=200),
                    border=ft.border.all(1, BORDER_COLOR),
                    border_radius=10,
                    padding=10,
                    bgcolor=CARD_COLOR
                )
            ], expand=True)
        ], spacing=20)
        
        historico = ft.Column([
            ft.Text("HISTÓRICO", size=18, weight="bold", color=TEXT_COLOR),
            pesquisa,
            filtros,
            ft.Container(
                content=ft.ListView([self.tabela], expand=True),
                border=ft.border.all(1, BORDER_COLOR),
                border_radius=10,
                padding=10,
                bgcolor=CARD_COLOR
            )
        ], spacing=10)
        
        self.page.add(
            ft.Column([
                ft.Text("CONTROLE FINANCEIRO", size=24, weight="bold", 
                       color=TEXT_COLOR, text_align="center"),
                form_card,
                ft.Container(
                    content=totais,
                    alignment=ft.alignment.center
                ),
                relatorios,
                historico
            ], spacing=25, expand=True)
        )
        
        self.atualizar_interface()

def main(page: ft.Page):
    ControleFinanceiro(page)

if __name__ == "__main__":
    ft.app(target=main)
