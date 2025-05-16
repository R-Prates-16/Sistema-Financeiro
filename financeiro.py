import flet as ft
import csv
from datetime import datetime
from collections import defaultdict
import os

# Configurações de estilo
PRIMARY_COLOR = "#4a6fa5"
SECONDARY_COLOR = "#166088"
BACKGROUND_COLOR = "#f8f9fa"
CARD_COLOR = "#ffffff"
TEXT_COLOR = "#343a40"
SUCCESS_COLOR = "#28a745"
ERROR_COLOR = "#dc3545"
WARNING_COLOR = "#ffc107"
BORDER_COLOR = "#dee2e6"

class Transacao:
    def __init__(self, descricao, valor, data, tipo):
        self.descricao = descricao
        self.valor = float(valor)
        self.data = data
        self.tipo = tipo  # 'receita' ou 'despesa'
        self.id = datetime.now().timestamp()  # ID único para cada transação

class ControleFinanceiro:
    def __init__(self, page):
        self.page = page
        self.setup_page()
        self.transacoes = []
        self.carregar_dados()
        self.criar_componentes()
        self.montar_layout()

    def setup_page(self):
        self.page.title = "Controle Financeiro Pessoal"
        self.page.window_width = 1100
        self.page.window_height = 800
        self.page.bgcolor = BACKGROUND_COLOR
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

    def mostrar_mensagem(self, mensagem, tipo="sucesso"):
        cores = {
            "sucesso": SUCCESS_COLOR,
            "erro": ERROR_COLOR,
            "aviso": WARNING_COLOR
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
                            row['tipo']
                        )
                        if 'id' in row:  # Para compatibilidade com versões anteriores
                            transacao.id = float(row['id'])
                        self.transacoes.append(transacao)
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao carregar dados: {str(e)}", "erro")

    def salvar_dados(self):
        try:
            with open("financas.csv", mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['id', 'descricao', 'valor', 'data', 'tipo'])
                writer.writeheader()
                for transacao in self.transacoes:
                    writer.writerow({
                        'id': transacao.id,
                        'descricao': transacao.descricao,
                        'valor': transacao.valor,
                        'data': transacao.data,
                        'tipo': transacao.tipo
                    })
        except Exception as e:
            self.mostrar_mensagem(f"Erro ao salvar dados: {str(e)}", "erro")

    def adicionar_transacao(self, e):
        descricao = self.input_descricao.value.strip()
        valor = self.input_valor.value.replace(",", ".").strip()
        data = self.input_data.value.strip() or datetime.now().strftime("%d/%m/%Y")
        tipo = self.select_tipo.value

        if not descricao or not valor:
            self.mostrar_mensagem("Preencha todos os campos obrigatórios!", "aviso")
            return

        try:
            valor_float = float(valor)
            if valor_float <= 0:
                self.mostrar_mensagem("O valor deve ser positivo!", "aviso")
                return

            datetime.strptime(data, "%d/%m/%Y")  # Validação da data

            nova_transacao = Transacao(descricao, valor_float, data, tipo)
            self.transacoes.append(nova_transacao)
            self.salvar_dados()
            
            self.input_descricao.value = ""
            self.input_valor.value = ""
            self.atualizar_interface()
            self.mostrar_mensagem("Transação adicionada com sucesso!")
            
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

    def calcular_totais(self):
        receitas = sum(t.valor for t in self.transacoes if t.tipo == 'receita')
        despesas = sum(t.valor for t in self.transacoes if t.tipo == 'despesa')
        saldo = receitas - despesas
        return receitas, despesas, saldo

    def calcular_lucros_por_periodo(self):
        # Cálculo de lucro mensal e anual
        lucro_mensal = defaultdict(float)
        lucro_anual = defaultdict(float)
        
        for transacao in self.transacoes:
            try:
                data = datetime.strptime(transacao.data, "%d/%m/%Y")
                mes_ano = data.strftime("%m/%Y")
                ano = data.strftime("%Y")
                
                if transacao.tipo == 'receita':
                    lucro_mensal[mes_ano] += transacao.valor
                    lucro_anual[ano] += transacao.valor
                else:
                    lucro_mensal[mes_ano] -= transacao.valor
                    lucro_anual[ano] -= transacao.valor
            except:
                continue
        
        return lucro_mensal, lucro_anual

    def criar_componentes(self):
        # Componentes de entrada
        self.input_descricao = ft.TextField(
            label="Descrição",
            expand=True,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        
        self.input_valor = ft.TextField(
            label="Valor (R$)",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_text="R$ ",
            width=200,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        
        self.input_data = ft.TextField(
            label="Data (dd/mm/aaaa)",
            value=datetime.now().strftime("%d/%m/%Y"),
            width=200,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )
        
        self.select_tipo = ft.Dropdown(
            label="Tipo",
            options=[
                ft.dropdown.Option("receita", "Receita"),
                ft.dropdown.Option("despesa", "Despesa"),
            ],
            value="receita",
            width=200,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )

        # Botões
        self.btn_adicionar = ft.ElevatedButton(
            "Adicionar Transação",
            icon="add",
            on_click=self.adicionar_transacao,
            bgcolor=PRIMARY_COLOR,
            color="white",
            height=45
        )
        
        self.btn_limpar = ft.TextButton(
            text="Limpar Campos",
            icon="clear",
            on_click=self.limpar_campos,
            style=ft.ButtonStyle(color=SECONDARY_COLOR)
        )

        # Cards de totais
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
                    ft.Text("TOTAL RECEITAS", size=14, color=TEXT_COLOR, weight="bold"),
                    ft.Text("R$ 0.00", size=24, color=SUCCESS_COLOR, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ),
            elevation=3
        )

        self.card_despesas = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("TOTAL DESPESAS", size=14, color=TEXT_COLOR, weight="bold"),
                    ft.Text("R$ 0.00", size=24, color=ERROR_COLOR, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ),
            elevation=3
        )

        self.card_saldo = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("SALDO ATUAL", size=14, color=TEXT_COLOR, weight="bold"),
                    ft.Text("R$ 0.00", size=24, weight="bold")
                ], alignment="center", horizontal_alignment="center"),
                **card_style
            ),
            elevation=3
        )

        # Tabela de transações
        self.tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Descrição", weight="bold")),
                ft.DataColumn(ft.Text("Valor (R$)", weight="bold")),
                ft.DataColumn(ft.Text("Data", weight="bold")),
                ft.DataColumn(ft.Text("Tipo", weight="bold")),
                ft.DataColumn(ft.Text("Ações", weight="bold")),
            ],
            border=ft.border.all(1, BORDER_COLOR),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, BORDER_COLOR),
            horizontal_lines=ft.border.BorderSide(1, BORDER_COLOR),
        )

        # Componentes de relatórios
        self.relatorio_mensal = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Mês/Ano", weight="bold")),
                ft.DataColumn(ft.Text("Lucro", weight="bold")),
            ],
            border=ft.border.all(1, BORDER_COLOR),
            border_radius=10
        )

        self.relatorio_anual = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Ano", weight="bold")),
                ft.DataColumn(ft.Text("Lucro", weight="bold")),
            ],
            border=ft.border.all(1, BORDER_COLOR),
            border_radius=10
        )

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
        receitas, despesas, saldo = self.calcular_totais()
        lucro_mensal, lucro_anual = self.calcular_lucros_por_periodo()
        
        # Atualizar cards
        self.card_receitas.content.content.controls[1].value = f"R$ {receitas:.2f}"
        self.card_despesas.content.content.controls[1].value = f"R$ {despesas:.2f}"
        self.card_saldo.content.content.controls[1].value = f"R$ {saldo:.2f}"
        self.card_saldo.content.content.controls[1].color = SUCCESS_COLOR if saldo >= 0 else ERROR_COLOR
        
        # Atualizar tabela de transações
        linhas = []
        for transacao in sorted(self.transacoes, key=lambda x: datetime.strptime(x.data, "%d/%m/%Y"), reverse=True):
            cor = SUCCESS_COLOR if transacao.tipo == 'receita' else ERROR_COLOR
            linhas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(transacao.descricao, color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(f"R$ {transacao.valor:.2f}", color=cor)),
                        ft.DataCell(ft.Text(transacao.data, color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(transacao.tipo.capitalize(), color=TEXT_COLOR)),
                        ft.DataCell(self.criar_botao_excluir(transacao.id))
                    ]
                )
            )
        
        self.tabela.rows = linhas
        
        # Atualizar relatórios
        linhas_mensal = []
        for mes_ano, lucro in sorted(lucro_mensal.items(), reverse=True):
            cor = SUCCESS_COLOR if lucro >= 0 else ERROR_COLOR
            linhas_mensal.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(mes_ano, color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(f"R$ {lucro:.2f}", color=cor))
                    ]
                )
            )
        self.relatorio_mensal.rows = linhas_mensal
        
        linhas_anual = []
        for ano, lucro in sorted(lucro_anual.items(), reverse=True):
            cor = SUCCESS_COLOR if lucro >= 0 else ERROR_COLOR
            linhas_anual.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(ano, color=TEXT_COLOR)),
                        ft.DataCell(ft.Text(f"R$ {lucro:.2f}", color=cor))
                    ]
                )
            )
        self.relatorio_anual.rows = linhas_anual
        
        self.page.update()

    def montar_layout(self):
        # Formulário de nova transação
        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("NOVA TRANSAÇÃO", size=18, weight="bold", color=PRIMARY_COLOR),
                    ft.Divider(height=10, color="transparent"),
                    ft.Row([self.input_descricao, self.input_valor]),
                    ft.Row([self.input_data, self.select_tipo]),
                    ft.Row([self.btn_limpar, self.btn_adicionar], alignment="end")
                ], spacing=10),
                padding=20,
                bgcolor=CARD_COLOR
            ),
            elevation=3,
            margin=ft.margin.only(bottom=20)
        )
        
        # Linha de totais
        totais_row = ft.Row(
            [self.card_receitas, self.card_despesas, self.card_saldo],
            alignment="spaceEvenly",
            spacing=20
        )
        
        # Linha de relatórios
        relatorios_row = ft.Row([
            ft.Column([
                ft.Text("LUCRO MENSAL", size=16, weight="bold", color=PRIMARY_COLOR),
                ft.Container(
                    content=ft.ListView([self.relatorio_mensal], height=200),
                    border=ft.border.all(1, BORDER_COLOR),
                    border_radius=10,
                    padding=10,
                    bgcolor=CARD_COLOR
                )
            ], expand=True),
            
            ft.Column([
                ft.Text("LUCRO ANUAL", size=16, weight="bold", color=PRIMARY_COLOR),
                ft.Container(
                    content=ft.ListView([self.relatorio_anual], height=200),
                    border=ft.border.all(1, BORDER_COLOR),
                    border_radius=10,
                    padding=10,
                    bgcolor=CARD_COLOR
                )
            ], expand=True)
        ], spacing=20)
        
        # Seção de histórico
        historico_section = ft.Column([
            ft.Text("HISTÓRICO DE TRANSAÇÕES", size=18, weight="bold", color=PRIMARY_COLOR),
            ft.Divider(height=10),
            ft.Container(
                content=ft.ListView([self.tabela], expand=True),
                border=ft.border.all(1, BORDER_COLOR),
                border_radius=10,
                padding=10,
                bgcolor=CARD_COLOR
            )
        ], spacing=10)
        
        # Layout principal
        self.page.add(
            ft.Column([
                ft.Text("CONTROLE FINANCEIRO", size=24, weight="bold", 
                       color=SECONDARY_COLOR, text_align="center"),
                form_card,
                totais_row,
                relatorios_row,
                historico_section
            ], spacing=25, expand=True)
        )
        
        self.atualizar_interface()

def main(page: ft.Page):
    ControleFinanceiro(page)

if __name__ == "__main__":
    ft.app(target=main)