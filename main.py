import sqlite3
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak
)


APP_NAME = "Controle Ariedam"

# =========================================================
# LOGO DO FUNDO
# =========================================================

LOGO_PATH = (
    Path(__file__).resolve().parent /
    "ariedam_logo.png"
)


DOWNLOAD_DIR = Path(
    "/storage/emulated/0/Download"
)

if DOWNLOAD_DIR.exists():

    BASE_DIR = (
        DOWNLOAD_DIR /
        "ARIEDAM_PDFs"
    )

else:

    BASE_DIR = (
        Path.cwd() /
        "ARIEDAM_PDFs"
    )


BASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DB_PATH = (
    BASE_DIR /
    "ariedam.db"
)

FUNCIONARIOS_PATH = (
    BASE_DIR /
    "funcionarios.txt"
)


SHEET_MAP = {

    "FUNCIONÁRIOS":
        "FUNCIONÁRIOS",

    "TRATORES":
        "TRATORES",

    "MORADORES, VISITANTES E FORNECEDORES":
        "COLABORADORES",

    "CAFÉ":
        "CAFÉ",
}


SHEET_TITLES = {

    "FUNCIONÁRIOS":
        "CONTROLE DE VEÍCULOS (FUNCIONÁRIOS)",

    "TRATORES":
        "CONTROLE DE VEÍCULOS (TRATORES)",

    "MORADORES, VISITANTES E FORNECEDORES":
        "MORADORES, VISITANTES E FORNECEDORES",

    "CAFÉ":
        "CONTROLE DE VEÍCULOS (CAFÉ)",
}


SHEETS = {

    "FUNCIONÁRIOS": [

        "MOTORISTA |",
        "DATA |",
        "PLACA |",
        "HORA \n ENTRADA |",
        "HORA \n SAÍDA |",
        "OBSERVAÇÕES"
    ],

    "TRATORES": [

        "MOTORISTA |",
        "DATA |",
        "PLACA |",
        "HORA \n ENTRADA",
        "HORA \n SAÍDA",
        "OBSERVAÇÕES"
    ],

    "MORADORES, VISITANTES E FORNECEDORES": [

        "NOME",
        "DATA",
        "PLACA",
        "HORA \n ENTRADA |",
        "HORA \n SAÍDA |",
        "OBSERVAÇÕES"
    ],

    "CAFÉ": [

        "MOTORISTA |",
        "DATA |",
        "PLACA |",
        "HORA \n ENTRADA |",
        "HORA \n SAÍDA |",
        "OBSERVAÇÕES"
    ],
}


COL_WIDTHS = [

    dp(140),
    dp(80),
    dp(90),
    dp(95),
    dp(90),
    dp(180)
]


TOTAL_WIDTH = sum(
    COL_WIDTHS
)


# =========================================================
# FUNCIONÁRIOS
# =========================================================

def init_funcionarios():

    if not FUNCIONARIOS_PATH.exists():

        FUNCIONARIOS_PATH.write_text(
            "# NOME | PLACA | OBSERVAÇÃO\n",
            encoding="utf-8"
        )


def get_funcionarios():

    init_funcionarios()

    funcionarios = []

    try:

        linhas = FUNCIONARIOS_PATH.read_text(
            encoding="utf-8"
        ).splitlines()

        for linha in linhas:

            linha = linha.strip()

            if (
                not linha
                or linha.startswith("#")
            ):
                continue

            partes = [
                x.strip()
                for x in linha.split("|")
            ]

            if len(partes) < 2:
                continue

            nome = partes[0]

            placa = partes[1]

            observacao = (
                partes[2]
                if len(partes) >= 3
                else ""
            )

            if nome:

                funcionarios.append(
                    (
                        nome,
                        placa,
                        observacao
                    )
                )

    except Exception:
        pass

    return funcionarios


def salvar_funcionario_txt(
    nome,
    placa,
    observacao
):

    init_funcionarios()

    nome = (
        nome.strip()
        .upper()
    )

    placa = (
        placa.strip()
        .upper()
    )

    observacao = (
        observacao.strip()
        .upper()
    )

    if not nome:
        return

    funcionarios = (
        get_funcionarios()
    )

    atualizado = False

    novas_linhas = []

    for funcionario in funcionarios:

        nome_existente = (
            funcionario[0]
        )

        if (
            nome_existente.upper()
            == nome
        ):

            novas_linhas.append(
                f"{nome} | "
                f"{placa} | "
                f"{observacao}"
            )

            atualizado = True

        else:

            novas_linhas.append(
                f"{funcionario[0]} | "
                f"{funcionario[1]} | "
                f"{funcionario[2]}"
            )

    if not atualizado:

        novas_linhas.append(
            f"{nome} | "
            f"{placa} | "
            f"{observacao}"
        )

    try:

        FUNCIONARIOS_PATH.write_text(
            "# NOME | PLACA | OBSERVAÇÃO\n"
            + "\n".join(novas_linhas)
            + "\n",
            encoding="utf-8"
        )

    except Exception:
        pass


def buscar_funcionarios_por_inicio(
    texto
):

    texto = (
        texto.strip()
        .upper()
    )

    if not texto:
        return []

    return [

        funcionario

        for funcionario
        in get_funcionarios()

        if funcionario[0]
        .upper()
        .startswith(texto)
    ]


# =========================================================
# BANCO
# =========================================================

def init_db():

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folha TEXT NOT NULL,
            campo1 TEXT,
            campo2 TEXT,
            campo3 TEXT,
            campo4 TEXT,
            campo5 TEXT,
            campo6 TEXT,
            criado_em TEXT NOT NULL
        )
    """)

    try:

        con.execute("""
            ALTER TABLE registros
            ADD COLUMN prioridade INTEGER DEFAULT 0
        """)

    except sqlite3.OperationalError:
        pass

    con.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT
        )
    """)

    existe = con.execute("""
        SELECT valor
        FROM configuracoes
        WHERE chave='nome_cafe'
    """).fetchone()

    if not existe:

        con.execute("""
            INSERT INTO configuracoes
            (chave, valor)
            VALUES ('nome_cafe', 'CAFÉ')
        """)

    con.commit()

    con.close()


def get_nome_cafe():

    con = sqlite3.connect(
        DB_PATH
    )

    row = con.execute("""
        SELECT valor
        FROM configuracoes
        WHERE chave='nome_cafe'
    """).fetchone()

    con.close()

    if row and row[0]:
        return row[0]

    return "CAFÉ"


def set_nome_cafe(nome):

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute("""
        INSERT INTO configuracoes
        (chave, valor)
        VALUES ('nome_cafe', ?)
        ON CONFLICT(chave)
        DO UPDATE SET valor=excluded.valor
    """, (nome,))

    con.commit()

    con.close()


def get_rows(sheet):

    con = sqlite3.connect(
        DB_PATH
    )

    rows = con.execute("""
        SELECT
            id,
            campo1,
            campo2,
            campo3,
            campo4,
            campo5,
            campo6,
            prioridade
        FROM registros
        WHERE folha=?
        ORDER BY id
    """, (sheet,)).fetchall()

    con.close()

    return rows


def get_row(row_id):

    con = sqlite3.connect(
        DB_PATH
    )

    row = con.execute("""
        SELECT
            id,
            folha,
            campo1,
            campo2,
            campo3,
            campo4,
            campo5,
            campo6,
            prioridade
        FROM registros
        WHERE id=?
    """, (row_id,)).fetchone()

    con.close()

    return row


def insert_row(
    sheet,
    values,
    prioridade=0
):

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute("""
        INSERT INTO registros
        (
            folha,
            campo1,
            campo2,
            campo3,
            campo4,
            campo5,
            campo6,
            criado_em,
            prioridade
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sheet,
        *values,
        datetime.now().isoformat(
            timespec="seconds"
        ),
        prioridade
    ))

    con.commit()

    con.close()


def update_row(
    row_id,
    values,
    prioridade=0
):

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute("""
        UPDATE registros
        SET
            campo1=?,
            campo2=?,
            campo3=?,
            campo4=?,
            campo5=?,
            campo6=?,
            prioridade=?
        WHERE id=?
    """, (
        *values,
        prioridade,
        row_id
    ))

    con.commit()

    con.close()


def delete_row(row_id):

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute(
        "DELETE FROM registros WHERE id=?",
        (row_id,)
    )

    con.commit()

    con.close()


def clear_all():

    con = sqlite3.connect(
        DB_PATH
    )

    con.execute(
        "DELETE FROM registros"
    )

    con.commit()

    con.close()


# =========================================================
# CABEÇALHO
# =========================================================

class HeaderLabel(Label):

    def __init__(self, **kwargs):

        super().__init__(
            **kwargs
        )

        with self.canvas.before:

            Color(
                0.35,
                0.35,
                0.35,
                1
            )

            self.rect = Rectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.update_rect,
            size=self.update_rect
        )

    def update_rect(
        self,
        *args
    ):

        self.rect.pos = self.pos

        self.rect.size = self.size


# =========================================================
# LINHA
# =========================================================

class DataRow(BoxLayout):

    def __init__(
        self,
        sheet,
        row,
        edit_callback,
        **kwargs
    ):

        super().__init__(
            orientation="horizontal",
            size_hint=(None, None),
            width=TOTAL_WIDTH,
            height=dp(45),
            spacing=dp(1),
            **kwargs
        )

        self.row_id = row[0]

        vals = row[1:7]

        prioridade = (
            row[7]
            if len(row) > 7
            else 0
        )

        for i, value in enumerate(
            vals
        ):

            texto = value or (

                "PENDENTE"
                if i == 4
                else ""
            )

            if prioridade == 1:

                fundo = (
                    0.20,
                    0.75,
                    0.35,
                    1
                )

            else:

                fundo = (
                    1,
                    1,
                    1,
                    1
                )

            botao = Button(
                text=texto,
                size_hint=(None, None),
                width=COL_WIDTHS[i],
                height=dp(45),
                font_size="12sp",
                color=(
                    0,
                    0,
                    0,
                    1
                ),
                background_normal="",
                background_color=fundo
            )

            botao.bind(
                on_release=lambda *_,
                rid=self.row_id:
                edit_callback(rid)
            )

            self.add_widget(
                botao
            )


# =========================================================
# BOX NO TOPO
# =========================================================

def criar_area_topo():

    area = BoxLayout(
        orientation="vertical",
        size_hint_y=None
    )

    area.bind(
        minimum_height=
        area.setter("height")
    )

    return area


# =========================================================
# FOLHA
# =========================================================

class SheetView(BoxLayout):

    def __init__(
        self,
        sheet_name,
        refresh_callback,
        **kwargs
    ):

        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(8),
            **kwargs
        )

        self.sheet_name = sheet_name

        self.refresh_callback = (
            refresh_callback
        )

        self.title_widget = Label(
            markup=True,
            size_hint_y=None,
            height=dp(36),
            font_size="16sp",
            halign="center",
            valign="middle"
        )

        self.title_widget.bind(
            size=self.title_widget.setter(
                "text_size"
            )
        )

        self.add_widget(
            self.title_widget
        )

        hint = Label(
            text=
            "Deslize a tabela para a direita | "
            "Toque para editar",
            size_hint_y=None,
            height=dp(24),
            font_size="13sp",
            halign="center"
        )

        hint.bind(
            size=hint.setter(
                "text_size"
            )
        )

        self.add_widget(
            hint
        )

        table_container = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=TOTAL_WIDTH
        )

        table_container.bind(
            minimum_height=
            table_container.setter(
                "height"
            )
        )

        self.header = GridLayout(
            cols=6,
            size_hint=(None, None),
            width=TOTAL_WIDTH,
            height=dp(50),
            spacing=dp(1)
        )

        for i, header in enumerate(
            SHEETS[sheet_name]
        ):

            texto = (
                header
                .replace("|", "")
                .strip()
            )

            if texto == "MOTORISTA":

                texto = (
                    "NOME MOTORISTA"
                )

            self.header.add_widget(
                HeaderLabel(
                    text=f"[b]{texto}[/b]",
                    markup=True,
                    color=(
                        1,
                        1,
                        1,
                        1
                    ),
                    size_hint=(None, None),
                    width=COL_WIDTHS[i],
                    height=dp(50),
                    halign="center",
                    valign="middle"
                )
            )

        table_container.add_widget(
            self.header
        )

        self.rows_box = GridLayout(
            cols=1,
            spacing=dp(2),
            size_hint=(None, None),
            width=TOTAL_WIDTH
        )

        self.rows_box.bind(
            minimum_height=
            self.rows_box.setter(
                "height"
            )
        )

        table_container.add_widget(
            self.rows_box
        )

        self.main_scroll = ScrollView(
            do_scroll_x=True,
            do_scroll_y=True
        )

        self.main_scroll.add_widget(
            table_container
        )

        self.add_widget(
            self.main_scroll
        )

        actions = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(6)
        )

        novo = Button(
            text="NOVO REGISTRO",
            background_color=(
                0.15,
                0.5,
                0.25,
                1
            )
        )

        novo.bind(
            on_release=lambda *_:
            self.add_form()
        )

        buscar = Button(
            text="BUSCAR"
        )

        buscar.bind(
            on_release=lambda *_:
            self.abrir_busca()
        )

        actions.add_widget(
            novo
        )

        actions.add_widget(
            buscar
        )

        self.add_widget(
            actions
        )

        self.refresh()

    # =====================================================
    # TÍTULO
    # =====================================================

    def update_title(self):

        if self.sheet_name == "CAFÉ":

            titulo = (
                "CONTROLE DE VEÍCULOS "
                f"({get_nome_cafe()})"
            )

        else:

            titulo = SHEET_TITLES.get(
                self.sheet_name,
                self.sheet_name
            )

        self.title_widget.text = (
            f"[b]{titulo}[/b]"
        )

    # =====================================================
    # SUGESTÕES
    # =====================================================

    def mostrar_sugestoes(
        self,
        entrada_nome,
        inputs,
        popup_sugestoes
    ):

        texto = (
            entrada_nome.text
            .strip()
            .upper()
        )

        if self.sheet_name not in (
            "FUNCIONÁRIOS",
            "TRATORES"
        ):

            return

        lista = (
            popup_sugestoes.lista_sugestoes
        )

        # CORREÇÃO DO CRASH:
        # O ScrollView pertence ao popup.
        # Antes o código tentava usar a variável
        # local "sugestoes_scroll", que não existia
        # dentro desta função.
        scroll_sugestoes = (
            popup_sugestoes.scroll_sugestoes
        )

        lista.clear_widgets()

        if not texto:

            popup_sugestoes.dismiss()

            return

        encontrados = (
            buscar_funcionarios_por_inicio(
                texto
            )
        )

        if not encontrados:

            popup_sugestoes.dismiss()

            return

        for funcionario in encontrados:

            nome = funcionario[0]

            placa = funcionario[1]

            observacao = funcionario[2]

            if self.sheet_name == "TRATORES":

                texto_botao = nome

            else:

                texto_botao = (
                    f"{nome}   |   {placa}"
                )

            botao = Button(
                text=texto_botao,
                size_hint_y=None,
                height=dp(44),
                font_size="13sp"
            )

            def selecionar(
                instance,
                nome=nome,
                placa=placa,
                observacao=observacao
            ):

                inputs[0].text = nome

                if (
                    self.sheet_name
                    == "TRATORES"
                ):

                    inputs[5].text = (
                        "CAMPO"
                    )

                else:

                    inputs[2].text = placa

                    inputs[5].text = (
                        observacao
                    )

                popup_sugestoes.dismiss()

            botao.bind(
                on_release=selecionar
            )

            lista.add_widget(
                botao
            )

        def ajustar_lista(
            *args
        ):

            # A lista deve ter somente a altura necessária para os nomes.
            # Isso faz o primeiro funcionário ficar no topo do ScrollView.
            lista.height = lista.minimum_height

        lista.bind(
            minimum_height=ajustar_lista
        )

        scroll_sugestoes.bind(
            size=ajustar_lista
        )

        ajustar_lista()

        scroll_sugestoes.scroll_y = 1

        # CORREÇÃO DE COMPATIBILIDADE:
        # Não dependemos de "_window" para saber
        # se o Popup está aberto.
        if not getattr(
            popup_sugestoes,
            "_is_open",
            False
        ):

            popup_sugestoes.open()

    # =====================================================
    # NOVO REGISTRO
    # =====================================================

    def add_form(self):

        box = criar_area_topo()

        inputs = []

        for idx, hint in enumerate(
            SHEETS[self.sheet_name]
        ):

            texto_hint = (
                hint
                .replace("|", "")
                .strip()
            )

            if texto_hint == "MOTORISTA":

                texto_hint = (
                    "NOME MOTORISTA"
                )

            label = Label(
                text=f"[b]{texto_hint}[/b]",
                markup=True,
                size_hint_y=None,
                height=dp(25),
                font_size="11sp",
                halign="left",
                valign="middle"
            )

            label.bind(
                size=label.setter(
                    "text_size"
                )
            )

            box.add_widget(
                label
            )

            entrada = TextInput(
                multiline=False,
                size_hint_y=None,
                height=dp(38)
            )

            if "DATA" in texto_hint:

                entrada.text = (
                    datetime.now()
                    .strftime("%d/%m/%Y")
                )

            elif (
                "HORA" in texto_hint
                and "ENTRADA" in texto_hint
            ):

                entrada.text = (
                    datetime.now()
                    .strftime("%H:%M")
                )

            box.add_widget(
                entrada
            )

            inputs.append(
                entrada
            )

        # -------------------------------------------------
        # POPUP DE SUGESTÕES
        # -------------------------------------------------

        sugestoes_lista = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(5),
            size_hint_y=None
        )

        sugestoes_lista.bind(
            minimum_height=
            sugestoes_lista.setter(
                "height"
            )
        )

        sugestoes_scroll = ScrollView(
            do_scroll_y=True,
            bar_width=dp(4)
        )

        sugestoes_scroll.add_widget(
            sugestoes_lista
        )

        popup_conteudo = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(8)
        )

        titulo_sugestoes = Label(
            text="[b]Funcionários encontrados:[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(32),
            font_size="14sp",
            halign="left",
            valign="middle"
        )

        titulo_sugestoes.bind(
            size=titulo_sugestoes.setter(
                "text_size"
            )
        )

        popup_conteudo.add_widget(
            titulo_sugestoes
        )

        popup_conteudo.add_widget(
            sugestoes_scroll
        )

        popup_sugestoes = Popup(
            title="",
            content=popup_conteudo,
            size_hint=(0.90, 0.55),
            auto_dismiss=True
        )

        popup_sugestoes.lista_sugestoes = (
            sugestoes_lista
        )

        popup_sugestoes.scroll_sugestoes = (
            sugestoes_scroll
        )

        if self.sheet_name in (
            "FUNCIONÁRIOS",
            "TRATORES"
        ):

            def pesquisar_nome(
                instance,
                value
            ):

                self.mostrar_sugestoes(
                    inputs[0],
                    inputs,
                    popup_sugestoes
                )

            inputs[0].bind(
                text=pesquisar_nome
            )

        # -------------------------------------------------
        # HORÁRIOS
        # -------------------------------------------------

        shortcuts = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6)
        )

        entrada_agora = Button(
            text="ENTRADA AGORA"
        )

        saida_agora = Button(
            text="SAÍDA AGORA"
        )

        shortcuts.add_widget(
            entrada_agora
        )

        shortcuts.add_widget(
            saida_agora
        )

        box.add_widget(
            shortcuts
        )

        entrada_agora.bind(
            on_release=lambda *_:
            setattr(
                inputs[3],
                "text",
                datetime.now().strftime(
                    "%H:%M"
                )
            )
        )

        saida_agora.bind(
            on_release=lambda *_:
            setattr(
                inputs[4],
                "text",
                datetime.now().strftime(
                    "%H:%M"
                )
            )
        )

        # -------------------------------------------------
        # PRIORIDADE
        # -------------------------------------------------

        prioridade_box = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )

        prioridade = CheckBox(
            size_hint_x=None,
            width=dp(40)
        )

        prioridade_box.add_widget(
            prioridade
        )

        prioridade_box.add_widget(
            Label(
                text="[b]PRIORIDADE[/b]",
                markup=True,
                font_size="12sp"
            )
        )

        box.add_widget(
            prioridade_box
        )

        # -------------------------------------------------
        # BOTÕES
        # -------------------------------------------------

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(6)
        )

        cancelar = Button(
            text="CANCELAR"
        )

        salvar = Button(
            text="SALVAR",
            background_color=(
                0.15,
                0.5,
                0.25,
                1
            )
        )

        botoes.add_widget(
            cancelar
        )

        botoes.add_widget(
            salvar
        )

        box.add_widget(
            botoes
        )

        nome_folha = (
            get_nome_cafe()
            if self.sheet_name == "CAFÉ"
            else SHEET_MAP.get(
                self.sheet_name,
                self.sheet_name
            )
        )

        scroll = ScrollView(
            do_scroll_y=True,
            bar_width=dp(4)
        )

        scroll.add_widget(
            box
        )

        popup = Popup(
            title=f"Novo Registro — {nome_folha}",
            content=scroll,
            size_hint=(0.95, 0.92)
        )

        cancelar.bind(
            on_release=popup.dismiss
        )

        def salvar_registro(*_):

            if not inputs[0].text.strip():

                return

            valores = [

                campo.text
                .strip()
                .upper()

                for campo in inputs
            ]

            if self.sheet_name == "TRATORES":

                valores[5] = "CAMPO"

            if self.sheet_name == "FUNCIONÁRIOS":

                salvar_funcionario_txt(
                    valores[0],
                    valores[2],
                    valores[5]
                )

            insert_row(
                self.sheet_name,
                valores,
                1
                if prioridade.active
                else 0
            )

            popup.dismiss()

            self.refresh()

        salvar.bind(
            on_release=salvar_registro
        )

        popup.open()

    # =====================================================
    # BUSCAR FUNCIONÁRIOS
    # =====================================================

    def abrir_busca(self):

        if self.sheet_name != "FUNCIONÁRIOS":

            return

        box = criar_area_topo()

        titulo = Label(
            text=
            "[b]Digite o nome do funcionário[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(28),
            halign="center"
        )

        titulo.bind(
            size=titulo.setter(
                "text_size"
            )
        )

        box.add_widget(
            titulo
        )

        entrada = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            hint_text="Nome do funcionário..."
        )

        box.add_widget(
            entrada
        )

        resultado_box = BoxLayout(
            orientation="vertical",
            spacing=dp(3),
            size_hint_y=None
        )

        resultado_box.bind(
            minimum_height=
            resultado_box.setter(
                "height"
            )
        )

        scroll_resultados = ScrollView(
            size_hint_y=None,
            height=dp(260)
        )

        scroll_resultados.add_widget(
            resultado_box
        )

        box.add_widget(
            scroll_resultados
        )

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(6)
        )

        fechar = Button(
            text="FECHAR"
        )

        botoes.add_widget(
            fechar
        )

        box.add_widget(
            botoes
        )

        scroll = ScrollView(
            do_scroll_y=True,
            bar_width=dp(4)
        )

        scroll.add_widget(
            box
        )

        popup = Popup(
            title="BUSCAR FUNCIONÁRIO",
            content=scroll,
            size_hint=(0.92, 0.70)
        )

        def pesquisar(*_):

            resultado_box.clear_widgets()

            texto = (
                entrada.text
                .strip()
                .upper()
            )

            if not texto:

                return

            registros = get_rows(
                "FUNCIONÁRIOS"
            )

            encontrados = []

            for registro in registros:

                nome = (
                    registro[1] or ""
                ).upper()

                if texto in nome:

                    encontrados.append(
                        registro
                    )

            if not encontrados:

                resultado_box.add_widget(
                    Label(
                        text=
                        "[b]Funcionário não encontrado.[/b]",
                        markup=True,
                        size_hint_y=None,
                        height=dp(45),
                        halign="center",
                        valign="middle"
                    )
                )

                return

            for registro in encontrados:

                nome = (
                    registro[1]
                    or ""
                )

                placa = (
                    registro[3]
                    or ""
                )

                botao = Button(
                    text=(
                        f"{nome}   |   "
                        f"{placa}"
                    ),
                    size_hint_y=None,
                    height=dp(45),
                    font_size="13sp"
                )

                def abrir_registro(
                    instance,
                    rid=registro[0]
                ):

                    popup.dismiss()

                    self.edit_form(
                        rid
                    )

                botao.bind(
                    on_release=abrir_registro
                )

                resultado_box.add_widget(
                    botao
                )

            scroll_resultados.scroll_y = 1

        entrada.bind(
            text=pesquisar
        )

        def fechar_busca(*_):

            popup.dismiss()

            self.refresh()

        fechar.bind(
            on_release=fechar_busca
        )

        popup.open()

    # =====================================================
    # EDITAR
    # =====================================================

    def edit_form(
        self,
        row_id
    ):

        row = get_row(
            row_id
        )

        if not row:

            return

        valores_atuais = list(
            row[2:8]
        )

        prioridade_atual = (
            row[8]
            if len(row) > 8
            else 0
        )

        box = criar_area_topo()

        inputs = []

        for idx, hint in enumerate(
            SHEETS[self.sheet_name]
        ):

            texto_hint = (
                hint
                .replace("|", "")
                .strip()
            )

            if texto_hint == "MOTORISTA":

                texto_hint = (
                    "NOME MOTORISTA"
                )

            label = Label(
                text=f"[b]{texto_hint}[/b]",
                markup=True,
                size_hint_y=None,
                height=dp(25),
                font_size="11sp",
                halign="left",
                valign="middle"
            )

            label.bind(
                size=label.setter(
                    "text_size"
                )
            )

            box.add_widget(
                label
            )

            entrada = TextInput(
                text=(
                    valores_atuais[idx]
                    or ""
                ),
                multiline=False,
                size_hint_y=None,
                height=dp(38)
            )

            if (
                "DATA" in texto_hint
                and not entrada.text.strip()
            ):

                entrada.text = (
                    datetime.now()
                    .strftime("%d/%m/%Y")
                )

            if self.sheet_name == "TRATORES":

                if idx == 5:

                    entrada.text = (
                        "CAMPO"
                    )

            inputs.append(
                entrada
            )

            box.add_widget(
                entrada
            )

        # -------------------------------------------------
        # SUGESTÕES
        # -------------------------------------------------

        sugestoes_lista = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(5),
            size_hint_y=None
        )

        sugestoes_lista.bind(
            minimum_height=
            sugestoes_lista.setter(
                "height"
            )
        )

        sugestoes_scroll = ScrollView(
            do_scroll_y=True,
            bar_width=dp(4)
        )

        sugestoes_scroll.add_widget(
            sugestoes_lista
        )

        popup_conteudo = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=dp(8)
        )

        titulo_sugestoes = Label(
            text="[b]Funcionários encontrados:[/b]",
            markup=True,
            size_hint_y=None,
            height=dp(32),
            font_size="14sp",
            halign="left",
            valign="middle"
        )

        titulo_sugestoes.bind(
            size=titulo_sugestoes.setter(
                "text_size"
            )
        )

        popup_conteudo.add_widget(
            titulo_sugestoes
        )

        popup_conteudo.add_widget(
            sugestoes_scroll
        )

        popup_sugestoes = Popup(
            title="",
            content=popup_conteudo,
            size_hint=(0.90, 0.55)
        )

        popup_sugestoes.lista_sugestoes = (
            sugestoes_lista
        )

        popup_sugestoes.scroll_sugestoes = (
            sugestoes_scroll
        )

        if self.sheet_name in (
            "FUNCIONÁRIOS",
            "TRATORES",
            "CAFÉ"
        ):

            def pesquisar_nome(
                instance,
                value
            ):

                self.mostrar_sugestoes(
                    inputs[0],
                    inputs,
                    popup_sugestoes
                )

            inputs[0].bind(
                text=pesquisar_nome
            )

        # -------------------------------------------------
        # SAÍDA
        # -------------------------------------------------

        atalhos = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6)
        )

        saida = Button(
            text="REGISTRAR SAÍDA AGORA"
        )

        atalhos.add_widget(
            saida
        )

        box.add_widget(
            atalhos
        )

        saida.bind(
            on_release=lambda *_:
            setattr(
                inputs[4],
                "text",
                datetime.now().strftime(
                    "%H:%M"
                )
            )
        )

        # -------------------------------------------------
        # PRIORIDADE
        # -------------------------------------------------

        prioridade_box = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8)
        )

        prioridade = CheckBox(
            size_hint_x=None,
            width=dp(40),
            active=(
                prioridade_atual == 1
            )
        )

        prioridade_box.add_widget(
            prioridade
        )

        prioridade_box.add_widget(
            Label(
                text="[b]PRIORIDADE[/b]",
                markup=True,
                font_size="12sp"
            )
        )

        box.add_widget(
            prioridade_box
        )

        # -------------------------------------------------
        # BOTÕES
        # -------------------------------------------------

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(6)
        )

        cancelar = Button(
            text="CANCELAR"
        )

        excluir = Button(
            text="EXCLUIR",
            background_color=(
                0.8,
                0.2,
                0.2,
                1
            )
        )

        salvar = Button(
            text="SALVAR",
            background_color=(
                0.15,
                0.5,
                0.25,
                1
            )
        )

        botoes.add_widget(
            cancelar
        )

        botoes.add_widget(
            excluir
        )

        botoes.add_widget(
            salvar
        )

        box.add_widget(
            botoes
        )

        scroll = ScrollView(
            do_scroll_y=True,
            bar_width=dp(4)
        )

        scroll.add_widget(
            box
        )

        popup = Popup(
            title="Editar Registro",
            content=scroll,
            size_hint=(0.95, 0.94)
        )

        cancelar.bind(
            on_release=popup.dismiss
        )

        def salvar_edicao(*_):

            valores = [

                campo.text
                .strip()
                .upper()

                for campo in inputs
            ]

            if self.sheet_name == "TRATORES":

                valores[5] = "CAMPO"

            update_row(
                row_id,
                valores,
                1
                if prioridade.active
                else 0
            )

            if self.sheet_name == "FUNCIONÁRIOS":

                salvar_funcionario_txt(
                    valores[0],
                    valores[2],
                    valores[5]
                )

            popup.dismiss()

            self.refresh()

        def excluir_registro(*_):

            delete_row(
                row_id
            )

            popup.dismiss()

            self.refresh()

        salvar.bind(
            on_release=salvar_edicao
        )

        excluir.bind(
            on_release=excluir_registro
        )

        popup.open()

    # =====================================================
    # ATUALIZAR TELA
    # =====================================================

    def refresh(self):

        self.update_title()

        self.rows_box.clear_widgets()

        for row in get_rows(
            self.sheet_name
        ):

            self.rows_box.add_widget(
                DataRow(
                    self.sheet_name,
                    row,
                    self.edit_form
                )
            )


# =========================================================
# TELA PRINCIPAL
# =========================================================

class MainScreen(BoxLayout):

    def __init__(
        self,
        **kwargs
    ):

        super().__init__(
            orientation="vertical",
            spacing=0,
            **kwargs
        )

        self.views = {}

        self.tab_buttons = {}

        tabs = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(2)
        )

        items = list(
            SHEET_MAP.items()
        )

        for internal_name, button_text in items:

            if internal_name == "CAFÉ":

                button_text = (
                    get_nome_cafe()
                )

            btn = Button(
                text=f"[b]{button_text}[/b]",
                markup=True,
                font_size="12sp",
                size_hint_x=1,
                background_normal="",
                background_color=(
                    0.18,
                    0.18,
                    0.18,
                    1
                ),
                color=(
                    1,
                    1,
                    1,
                    1
                )
            )

            self.tab_buttons[
                internal_name
            ] = btn

            view = SheetView(
                internal_name,
                self.refresh_all
            )

            self.views[
                internal_name
            ] = view

            if internal_name == "CAFÉ":

                btn.bind(
                    on_release=lambda *_:
                    self.abrir_cafe()
                )

            else:

                btn.bind(
                    on_release=lambda *_,
                    name=internal_name:
                    self.show_sheet(name)
                )

            tabs.add_widget(
                btn
            )

        self.add_widget(
            tabs
        )

        self.content = BoxLayout(
            orientation="vertical"
        )

        self.add_widget(
            self.content
        )

        self.show_sheet(
            "FUNCIONÁRIOS"
        )

    # =====================================================
    # CAFÉ
    # =====================================================

    def abrir_cafe(self):

        self.show_sheet(
            "CAFÉ"
        )

        App.get_running_app().editar_nome_cafe()

    # =====================================================
    # ABAS
    # =====================================================

    def show_sheet(
        self,
        sheet_name
    ):

        self.content.clear_widgets()

        self.content.add_widget(
            self.views[sheet_name]
        )

        for name, button in (
            self.tab_buttons.items()
        ):

            if name == sheet_name:

                button.background_color = (
                    0.20,
                    0.75,
                    0.35,
                    1
                )

            else:

                button.background_color = (
                    0.18,
                    0.18,
                    0.18,
                    1
                )

    # =====================================================
    # ATUALIZAR
    # =====================================================

    def refresh_all(self):

        if "CAFÉ" in self.tab_buttons:

            self.tab_buttons[
                "CAFÉ"
            ].text = (
                f"[b]{get_nome_cafe()}[/b]"
            )

        for view in self.views.values():

            view.refresh()


# =========================================================
# APLICATIVO
# =========================================================

class AriedamApp(App):

    title = APP_NAME

    def build(self):

        init_db()

        init_funcionarios()

        Window.softinput_mode = (
            "below_target"
        )

        # =================================================
        # ROOT COM FUNDO
        # =================================================

        root = FloatLayout()

        # -------------------------------------------------
        # LOGO DE FUNDO
        # -------------------------------------------------

        if LOGO_PATH.exists():

            logo_background = Image(
                source=str(LOGO_PATH),
                size_hint=(1, 1),
                pos_hint={
                    "x": 0,
                    "y": 0
                },
                allow_stretch=True,
                keep_ratio=False,
                opacity=0.65
            )

            root.add_widget(
                logo_background
            )

        else:

            fundo = Widget(
                size_hint=(1, 1),
                pos_hint={
                    "x": 0,
                    "y": 0
                }
            )

            with fundo.canvas.before:

                Color(
                    0.08,
                    0.08,
                    0.08,
                    1
                )

                Rectangle(
                    pos=fundo.pos,
                    size=fundo.size
                )

            root.add_widget(
                fundo
            )

        # =================================================
        # CONTEÚDO PRINCIPAL
        # =================================================

        foreground = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            pos_hint={
                "x": 0,
                "y": 0
            }
        )

        self.main = MainScreen()

        foreground.add_widget(
            self.main
        )

        # =================================================
        # BARRA INFERIOR
        # =================================================

        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(6),
            padding=dp(6)
        )

        pdf = Button(
            text="GERAR PDF COMPLETO",
            background_color=(
                0.15,
                0.4,
                0.7,
                1
            )
        )

        pdf.bind(
            on_release=lambda *_:
            self.generate_pdf()
        )

        limpar = Button(
            text="LIMPAR APÓS SALVAR",
            background_color=(
                0.7,
                0.2,
                0.2,
                1
            )
        )

        limpar.bind(
            on_release=lambda *_:
            self.confirm_clear()
        )

        bottom.add_widget(
            pdf
        )

        bottom.add_widget(
            limpar
        )

        foreground.add_widget(
            bottom
        )

        root.add_widget(
            foreground
        )

        return root

    # =====================================================
    # NOME DO CAFÉ
    # =====================================================

    def editar_nome_cafe(self):

        box = criar_area_topo()

        box.add_widget(
            Label(
                text="[b]Digite o novo nome:[/b]",
                markup=True,
                size_hint_y=None,
                height=dp(28),
                halign="center"
            )
        )

        entrada = TextInput(
            text=get_nome_cafe(),
            multiline=False,
            size_hint_y=None,
            height=dp(42)
        )

        box.add_widget(
            entrada
        )

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(44),
            spacing=dp(6)
        )

        cancelar = Button(
            text="CANCELAR"
        )

        salvar = Button(
            text="SALVAR",
            background_color=(
                0.15,
                0.5,
                0.25,
                1
            )
        )

        botoes.add_widget(
            cancelar
        )

        botoes.add_widget(
            salvar
        )

        box.add_widget(
            botoes
        )

        scroll = ScrollView(
            do_scroll_y=True,
            bar_width=dp(4)
        )

        scroll.add_widget(
            box
        )

        popup = Popup(
            title="ALTERAR NOME DO CAFÉ",
            content=scroll,
            size_hint=(0.90, 0.42)
        )

        cancelar.bind(
            on_release=popup.dismiss
        )

        def salvar_nome(*_):

            novo_nome = (
                entrada.text
                .strip()
                .upper()
            )

            if not novo_nome:

                return

            set_nome_cafe(
                novo_nome
            )

            popup.dismiss()

            self.main.refresh_all()

        salvar.bind(
            on_release=salvar_nome
        )

        popup.open()

    # =====================================================
    # PDF
    # =====================================================

    def generate_pdf(self):

        stamp = datetime.now().strftime(
            "%Y-%m-%d"
        )

        path = (
            BASE_DIR /
            f"Controle_Ariedam_{stamp}.pdf"
        )

        styles = getSampleStyleSheet()

        small = ParagraphStyle(
            "SmallA",
            parent=styles["BodyText"],
            fontSize=7,
            leading=8
        )

        header_left = ParagraphStyle(
            "HeaderLeft",
            parent=styles["BodyText"],
            alignment=TA_CENTER,
            fontSize=8,
            leading=9
        )

        header_title = ParagraphStyle(
            "HeaderTitle",
            parent=styles["BodyText"],
            alignment=TA_CENTER,
            fontSize=9,
            leading=10
        )

        doc = SimpleDocTemplate(
            str(path),
            pagesize=landscape(A4),
            rightMargin=18,
            leftMargin=18,
            topMargin=18,
            bottomMargin=18
        )

        story = []

        MAX_REGISTROS = 20

        for sheet in SHEETS:

            rows = get_rows(
                sheet
            )

            if not rows:

                grupos = [[]]

            else:

                grupos = [

                    rows[
                        i:i + MAX_REGISTROS
                    ]

                    for i in range(
                        0,
                        len(rows),
                        MAX_REGISTROS
                    )
                ]

            for folha_num, grupo in enumerate(
                grupos,
                start=1
            ):

                pdf_headers = [

                    h.replace(
                        "|",
                        ""
                    ).strip()

                    for h in SHEETS[sheet]
                ]

                if (
                    pdf_headers[0]
                    == "MOTORISTA"
                ):

                    pdf_headers[0] = (
                        "NOME MOTORISTA"
                    )

                if sheet == "CAFÉ":

                    titulo = (
                        "CONTROLE DE VEÍCULOS "
                        f"({get_nome_cafe()})"
                    )

                else:

                    titulo = (
                        SHEET_TITLES.get(
                            sheet,
                            sheet
                        )
                    )

                data = [

                    [

                        Paragraph(
                            "<b>ARIEDAM</b><br/>"
                            "NOSSO FOCO É AGRO",
                            header_left
                        ),

                        Paragraph(
                            f"<b>{titulo}</b>",
                            header_title
                        ),

                        "",
                        "",
                        "",
                        ""
                    ],

                    [

                        Paragraph(
                            f"<b>{pdf_headers[0]}</b>",
                            small
                        ),

                        Paragraph(
                            f"<b>{pdf_headers[1]}</b>",
                            small
                        ),

                        Paragraph(
                            f"<b>{pdf_headers[2]}</b>",
                            small
                        ),

                        Paragraph(
                            f"<b>{pdf_headers[3]}</b>",
                            small
                        ),

                        Paragraph(
                            f"<b>{pdf_headers[4]}</b>",
                            small
                        ),

                        Paragraph(
                            f"<b>{pdf_headers[5]}</b>",
                            small
                        )
                    ]
                ]

                for r in grupo:

                    data.append(
                        list(r[1:7])
                    )

                if len(data) == 2:

                    data.append(
                        [""] * 6
                    )

                table = Table(
                    data,
                    colWidths=[
                        120,
                        70,
                        90,
                        80,
                        80,
                        250
                    ],
                    repeatRows=2
                )

                table.setStyle(
                    TableStyle([

                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.black
                        ),

                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 1),
                            colors.HexColor(
                                "#E6E6E6"
                            )
                        ),

                        (
                            "SPAN",
                            (1, 0),
                            (-1, 0)
                        ),

                        (
                            "FONTNAME",
                            (0, 0),
                            (-1, 1),
                            "Helvetica-Bold"
                        ),

                        (
                            "FONTSIZE",
                            (0, 2),
                            (-1, -1),
                            7
                        ),

                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE"
                        ),

                        (
                            "ALIGN",
                            (0, 0),
                            (-1, -1),
                            "CENTER"
                        ),

                        (
                            "ROWBACKGROUNDS",
                            (0, 2),
                            (-1, -1),
                            [
                                colors.white,
                                colors.HexColor(
                                    "#F8F8F8"
                                )
                            ]
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, 1),
                            4
                        ),

                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, 1),
                            4
                        ),

                        (
                            "BOTTOMPADDING",
                            (0, 2),
                            (-1, -1),
                            5
                        ),

                        (
                            "TOPPADDING",
                            (0, 2),
                            (-1, -1),
                            5
                        ),
                    ])
                )

                story.append(
                    table
                )

                story.append(
                    Spacer(1, 6)
                )

                story.append(
                    Paragraph(
                        "Observações: "
                        "________________________________"
                        "________________________________"
                        "________________________________",
                        small
                    )
                )

                story.append(
                    Spacer(1, 8)
                )

                story.append(
                    Paragraph(
                        f"{titulo} — "
                        f"FOLHA {folha_num:02d} • "
                        f"Gerado em "
                        f"{datetime.now().strftime('%d/%m/%Y')}",
                        small
                    )
                )

                story.append(
                    PageBreak()
                )

        if (
            story
            and isinstance(
                story[-1],
                PageBreak
            )
        ):

            story.pop()

        doc.build(
            story
        )

        self.show_message(
            "PDF criado com sucesso!",
            f"Arquivo salvo na pasta:\n{path}"
        )

    # =====================================================
    # LIMPAR
    # =====================================================

    def confirm_clear(self):

        box = criar_area_topo()

        box.add_widget(
            Label(
                text=
                "Confirme que o PDF já foi gerado.\n\n"
                "Isso apagará os registros das 4 folhas "
                "do banco local.",
                size_hint_y=None,
                height=dp(70),
                halign="center",
                valign="middle"
            )
        )

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(46),
            spacing=dp(6)
        )

        nao = Button(
            text="CANCELAR"
        )

        sim = Button(
            text="LIMPAR TUDO",
            background_color=(
                0.8,
                0.2,
                0.2,
                1
            )
        )

        botoes.add_widget(
            nao
        )

        botoes.add_widget(
            sim
        )

        box.add_widget(
            botoes
        )

        popup = Popup(
            title="CONFIRMAR LIMPEZA",
            content=box,
            size_hint=(0.88, 0.42)
        )

        nao.bind(
            on_release=popup.dismiss
        )

        def limpar(*_):

            clear_all()

            popup.dismiss()

            self.main.refresh_all()

            self.show_message(
                "Pronto",
                "As 4 folhas foram limpas para o próximo dia."
            )

        sim.bind(
            on_release=limpar
        )

        popup.open()

    # =====================================================
    # MENSAGEM
    # =====================================================

    def show_message(
        self,
        title,
        msg
    ):

        box = criar_area_topo()

        box.add_widget(
            Label(
                text=msg,
                size_hint_y=None,
                height=dp(80),
                halign="center",
                valign="middle"
            )
        )

        ok = Button(
            text="OK",
            size_hint_y=None,
            height=dp(40)
        )

        box.add_widget(
            ok
        )

        popup = Popup(
            title=title,
            content=box,
            size_hint=(0.92, 0.45)
        )

        ok.bind(
            on_release=popup.dismiss
        )

        popup.open()


# =========================================================
# INICIAR
# =========================================================

if __name__ == "__main__":

    AriedamApp().run()
