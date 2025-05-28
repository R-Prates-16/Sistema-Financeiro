import flet as ft  # Framework para interface gráfica
import csv  # Para manipulação de arquivos CSV
from datetime import datetime  # Para trabalhar com datas
from collections import defaultdict  # Para dicionários com valores padrão
import os  # Para operações do sistema operacional

# ================== CONFIGURAÇÕES GERAIS ================== #
# Cores utilizadas no aplicativo
PRIMARY_COLOR = "#4a6fa5"  # Cor primária (azul)
SECONDARY_COLOR = "#166088"  # Cor secundária (azul mais escuro)
BACKGROUND_COLOR = "#f8f9fa"  # Cor de fundo
CARD_COLOR = "#ffffff"  # Cor dos cards
TEXT_COLOR = "#212121"  # Cor do texto
SUCCESS_COLOR = "#28a745"  # Cor para sucesso (verde)
ERROR_COLOR = "#dc3545"  # Cor para erro (vermelho)
WARNING_COLOR = "#ffc107"  # Cor para aviso (amarelo)
BORDER_COLOR = "#dee2e6"  # Cor das bordas
INVESTMENT_COLOR = "#6f42c1"  # Cor para investimentos (roxo)
SEARCH_HIGHLIGHT_COLOR = "#ffeb3b"  # Cor para destacar resultados de busca

# Categorias pré-definidas para cada tipo de transação
CATEGORIAS = {
    "receita": ["Salário", "Freelance", "Investimentos", "Outros"],
    "despesa": ["Alimentação", "Moradia", "Transporte", "Lazer", "Saúde", "Educação", "Outros"],
    "investimento": ["Ações", "Fundos", "Renda Fixa", "Criptomoedas", "Outros"]
}

def carregar_logo():
    """Função para carregar o logo do aplicativo"""
    try:
        # Verifica se o arquivo de logo existe
        if os.path.exists("logo.png"):
            return ft.Image(src="logo.png", width=50, height=50, fit=ft.ImageFit.CONTAIN)
        else:
            # Retorna um ícone padrão se o logo não existir
            return ft.Icon(name="account_balance", color=PRIMARY_COLOR, size=40)
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")
        return ft.Icon(name="account_balance", color=PRIMARY_COLOR, size=40)

# ================== MODELO DE DADOS ================== #
class Transacao:
    """Classe que representa uma transação financeira"""
    def __init__(self, descricao, valor, data, tipo, categoria):
        self.descricao = descricao  # Descrição da transação
        self.valor = float(valor)  # Valor da transação (convertido para float)
        self.data = data  # Data da transação no formato dd/mm/aaaa
        self.tipo = tipo  # Tipo: receita, despesa ou investimento
        self.categoria = categoria  # Categoria da transação
        self.id = datetime.now().timestamp()  # ID único baseado no timestamp

# ================== CONTROLE PRINCIPAL ================== #
class ControleFinanceiro:
    """Classe principal que controla a aplicação"""
    def __init__(self, page):
        self.page = page  # Página principal do Flet
        self.setup_page()  # Configura a página
        self.transacoes = []  # Lista para armazenar todas as transações
        self.filtro_ativo = "todos"  # Filtro ativo inicialmente
        self.termo_pesquisa = ""  # Termo de pesquisa vazio inicialmente
        self.carregar_dados()  # Carrega dados do arquivo CSV
        self.criar_componentes()  # Cria os componentes da interface
        self.montar_layout()  # Monta o layout da interface

    def setup_page(self):
        """Configura as propriedades básicas da página"""
        self.page.title = "Controle Financeiro Pessoal"
        self.page.window_width = 1200  # Largura da janela
        self.page.window_height = 850  # Altura da janela
        self.page.bgcolor = BACKGROUND_COLOR  # Cor de fundo
        self.page.padding = 20  # Espaçamento interno
        self.page.scroll = ft.ScrollMode.AUTO  # Habilita scroll automático

    def mostrar_mensagem(self, mensagem, tipo="sucesso"):
        """Exibe uma mensagem na tela (snackbar)"""
        # Define as cores com base no tipo de mensagem
        cores = {
            "sucesso": SUCCESS_COLOR,
            "erro": ERROR_COLOR,
            "aviso": WARNING_COLOR,
            "investimento": INVESTMENT_COLOR
        }
        # Cria e exibe a mensagem
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(mensagem, color="white"),
            bgcolor=cores[tipo],
            behavior=ft.SnackBarBehavior.FLOATING
        )
        self.page.snack_bar.open = True
        self.page.update()

    def carregar_dados(self):
        """Carrega as transações salvas no arquivo CSV"""
        try:
            if os.path.exists("financas.csv"):
                with open("financas.csv", mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Cria uma nova transação para cada linha do CSV
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
        """Salva as transações no arquivo CSV"""
        try:
            with open("financas.csv", mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['id', 'descricao', 'valor', 'data', 'tipo', 'categoria'])
                writer.writeheader()  # Escreve o cabeçalho
                for transacao in self.transacoes:
                    # Escreve cada transação como uma linha no CSV
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
        """Adiciona uma nova transação com base nos dados do formulário"""
        # Obtém os valores dos campos de entrada
        descricao = self.input_descricao.value.strip()
        valor = self.input_valor.value.replace(",", ".").strip()  # Substitui vírgula por ponto
        data = self.input_data.value.strip() or datetime.now().strftime("%d/%m/%Y")
        tipo = self.select_tipo.value
        categoria = self.select_categoria.value

        # Validação dos campos obrigatórios
        if not descricao or not valor:
            self.mostrar_mensagem("Preencha todos os campos obrigatórios!", "aviso")
            return

        try:
            valor_float = float(valor)
            if valor_float <= 0:
                self.mostrar_mensagem("O valor deve ser positivo!", "aviso")
                return

            # Valida o formato da data
            datetime.strptime(data, "%d/%m/%Y")

            # Cria e adiciona a nova transação
            nova_transacao = Transacao(descricao, valor_float, data, tipo, categoria)
            self.transacoes.append(nova_transacao)
            self.salvar_dados()  # Salva os dados no arquivo
            
            # Limpa os campos de entrada
            self.input_descricao.value = ""
            self.input_valor.value = ""
            self.atualizar_interface()  # Atualiza a interface
            
            # Mostra mensagem de sucesso com a cor correspondente ao tipo
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
        """Remove uma transação com base no ID"""
        self.transacoes = [t for t in self.transacoes if t.id != transacao_id]
        self.salvar_dados()
        self.atualizar_interface()
        self.mostrar_mensagem("Transação excluída com sucesso!")

    def aplicar_filtro(self, tipo):
        """Aplica um filtro para mostrar apenas um tipo específico de transação"""
        self.filtro_ativo = tipo
        self.atualizar_interface()

    def atualizar_categorias(self, e):
        """Atualiza as categorias disponíveis com base no tipo selecionado"""
        tipo = self.select_tipo.value
        # Atualiza as opções do dropdown de categorias
        self.select_categoria.options = [
            ft.dropdown.Option(cat) for cat in CATEGORIAS.get(tipo, ["Outros"])
        ]
        self.select_categoria.value = CATEGORIAS.get(tipo, ["Outros"])[0]
        self.page.update()

    def pesquisar_transacoes(self, e):
        """Filtra as transações com base no termo de pesquisa"""
        self.termo_pesquisa = self.input_pesquisa.value.lower().strip()
        self.atualizar_interface()

    def calcular_totais(self):
        """Calcula os totais de receitas, despesas, investimentos e saldo"""
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
        """Calcula o lucro mensal e anual"""
        lucro_mensal = defaultdict(float)  # Dicionário para lucro por mês/ano
        lucro_anual = defaultdict(float)  # Dicionário para lucro por ano
        
        for transacao in self.transacoes:
            try:
                # Define o sinal do valor (+ para receita, - para despesa/investimento)
                if transacao.tipo == 'despesa':
                    sinal = -1
                elif transacao.tipo == 'investimento':
                    sinal = -1  # Investimentos reduzem o lucro
                else:
                    sinal = 1
                
                # Processa a data
                data = datetime.strptime(transacao.data, "%d/%m/%Y")
                mes_ano = data.strftime("%m/%Y")
                ano = data.strftime("%Y")
                
                # Acumula os valores
                lucro_mensal[mes_ano] += transacao.valor * sinal
                lucro_anual[ano] += transacao.valor * sinal
            except:
                continue
        
        return lucro_mensal, lucro_anual

    def criar_componentes(self):
        """Cria todos os componentes da interface"""
        # Campos de entrada para nova transação
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

        # Campo de pesquisa
        self.input_pesquisa = ft.TextField(
            label="Pesquisar transações",
            prefix_icon="search",
            on_change=self.pesquisar_transacoes,
            expand=True,
            border_color=PRIMARY_COLOR,
            color=TEXT_COLOR
        )

        # Botões
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

        # Botões de filtro
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

        # Cards de resumo
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

        # Tabela de transações
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

        # Tabelas de relatórios
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
        """Destaca o termo de pesquisa no texto, se encontrado"""
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
        """Limpa os campos do formulário"""
        self.input_descricao.value = ""
        self.input_valor.value = ""
        self.input_data.value = datetime.now().strftime("%d/%m/%Y")
        self.page.update()

    def criar_botao_excluir(self, transacao_id):
        """Cria um botão de excluir para uma transação"""
        return ft.IconButton(
            icon="delete", 
            icon_color=ERROR_COLOR,
            tooltip="Excluir", 
            on_click=lambda e: self.excluir_transacao(transacao_id)
        )

    def atualizar_interface(self):
        """Atualiza toda a interface com os dados mais recentes"""
        # Calcula totais e lucros
        totais = self.calcular_totais()
        lucro_mensal, lucro_anual = self.calcular_lucros_por_periodo()
        
        # Atualiza cards com os novos valores
        self.card_receitas.content.content.controls[1].value = f"R$ {totais['receitas']:.2f}"
        self.card_despesas.content.content.controls[1].value = f"R$ {totais['despesas']:.2f}"
        self.card_saldo.content.content.controls[1].value = f"R$ {totais['saldo']:.2f}"
        # Define a cor do saldo (verde para positivo, vermelho para negativo)
        self.card_saldo.content.content.controls[1].color = SUCCESS_COLOR if totais['saldo'] >= 0 else ERROR_COLOR
        self.card_investimentos.content.content.controls[1].value = f"R$ {totais['investimentos']:.2f}"
        
        # Filtra as transações conforme o filtro ativo
        transacoes_filtradas = self.transacoes
        if self.filtro_ativo != "todos":
            transacoes_filtradas = [t for t in self.transacoes if t.tipo == self.filtro_ativo]
        
        # Aplica a pesquisa, se houver termo
        if self.termo_pesquisa:
            transacoes_filtradas = [t for t in transacoes_filtradas 
                                  if self.termo_pesquisa.lower() in t.descricao.lower()]
        
        # Cria as linhas da tabela com as transações filtradas
        linhas = []
        for transacao in sorted(transacoes_filtradas, 
                              key=lambda x: datetime.strptime(x.data, "%d/%m/%Y"), 
                              reverse=True):
            # Define a cor com base no tipo de transação
            cor = {
                "receita": SUCCESS_COLOR,
                "despesa": ERROR_COLOR,
                "investimento": INVESTMENT_COLOR
            }.get(transacao.tipo, TEXT_COLOR)
            
            # Cria uma linha da tabela para cada transação
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
        
        # Atualiza os relatórios mensais
        self.relatorio_mensal.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(mes_ano, color=TEXT_COLOR)),
                ft.DataCell(ft.Text(f"R$ {lucro:.2f}", 
                                  color=SUCCESS_COLOR if lucro >= 0 else ERROR_COLOR))
            ]) for mes_ano, lucro in sorted(lucro_mensal.items(), reverse=True)
        ]
        
        # Atualiza os relatórios anuais
        self.relatorio_anual.rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(ano, color=TEXT_COLOR)),
                ft.DataCell(ft.Text(f"R$ {lucro:.2f}", 
                                  color=SUCCESS_COLOR if lucro >= 0 else ERROR_COLOR))
            ]) for ano, lucro in sorted(lucro_anual.items(), reverse=True)
        ]
        
        # Atualiza a aparência dos botões de filtro
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
        """Monta o layout completo da aplicação"""
        # Cria o cabeçalho com logo e título
        header = ft.Row(
            [
                carregar_logo(),
                ft.Text("CONTROLE FINANCEIRO", size=24, weight="bold", 
                       color=TEXT_COLOR, text_align="center"),
            ],
            alignment="center",
            spacing=10
        )
        
        # Card do formulário de nova transação
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
        
        # Linha de botões de filtro
        filtros = ft.Row(
            [self.btn_filtro_todos, self.btn_filtro_receitas, 
             self.btn_filtro_despesas, self.btn_filtro_investimentos],
            spacing=10
        )
        
        # Campo de pesquisa
        pesquisa = ft.Row(
            [self.input_pesquisa],
            spacing=20,
            alignment="spaceBetween"
        )
        
        # Cards de resumo (centralizados)
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
        
        # Seção de relatórios (mensal e anual)
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
        
        # Seção do histórico de transações
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
        
        # Adiciona todos os componentes à página
        self.page.add(
            ft.Column([
                header,  # Cabeçalho com logo
                form_card,  # Formulário de nova transação
                ft.Container(
                    content=totais,
                    alignment=ft.alignment.center
                ),  # Cards de resumo
                relatorios,  # Relatórios
                historico  # Histórico de transações
            ], spacing=25, expand=True)
        )
        
        # Atualiza a interface com os dados iniciais
        self.atualizar_interface()

# Função principal que inicia a aplicação
def main(page: ft.Page):
    ControleFinanceiro(page)

# Ponto de entrada do programa
if __name__ == "__main__":
    ft.app(target=main)



#Este código implementa um sistema de controle financeiro pessoal utilizando o framework Flet para a interface gráfica. A lógica central é baseada na classe ControleFinanceiro, 
#que gerencia todas as operações do aplicativo. O sistema armazena transações financeiras (receitas, despesas e investimentos) como objetos da classe Transacao, cada um com 
#descrição, valor, data, tipo e categoria. Os dados são persistidos em um arquivo CSV, permitindo que as informações sejam mantidas entre execuções do programa. A interface é 
#organizada em seções distintas: um formulário para cadastro de novas transações, cards que exibem totais e saldo atual, tabelas de relatórios mensais/anuais e um histórico de 
#transações com filtros e busca. A navegação entre as funcionalidades é feita através de botões que atualizam dinamicamente a interface.

#A aplicação utiliza vários conceitos importantes de programação, como manipulação de arquivos (para salvar/carregar dados), tratamento de exceções (para validar entradas), 
#dicionários (para agrupar categorias) e programação orientada a objetos. A atualização da interface acontece de forma reativa - sempre que uma transação é adicionada, removida
#ou quando um filtro é aplicado, o método atualizar_interface() recalcula todos os totais, refiltra as transações e redesenha os componentes visuais. O sistema também implementa 
#uma função de destaque de texto para realçar os termos pesquisados nas descrições das transações, melhorando a experiência do usuário durante buscas.
