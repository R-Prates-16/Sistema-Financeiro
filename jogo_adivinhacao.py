import flet as ft
import random
import os
from datetime import datetime

DATA_FILE = "scores.txt"

def main(page: ft.Page):
    page.title = "🎯 Jogo de Adivinhação"
    page.bgcolor = "#1e1e2f"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.padding = 20
    page.window_width = 400
    page.window_height = 600

    target_number = None
    attempts = 0
    range_start = None
    range_end = None

    def styled_text(value, size=16, weight="normal", color="#FFF", center=False):
        return ft.Text(value, size=size, weight=weight, color=color, text_align="center" if center else "start")

    input_range_start = ft.TextField(
        label="Número Inicial",
        width=250,
        bgcolor="#121212",
        border_color="#444",
        focused_border_color="#00b894",
        text_style=ft.TextStyle(color="white", size=16),
    )
    input_range_end = ft.TextField(
        label="Número Final",
        width=250,
        bgcolor="#121212",
        border_color="#444",
        focused_border_color="#00b894",
        text_style=ft.TextStyle(color="white", size=16),
    )
    start_button = ft.ElevatedButton(
        "Iniciar Jogo",
        bgcolor="#00b894",
        color="white",
        width=250,
        height=45,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )

    guess_input = ft.TextField(
        label="Seu Palpite",
        width=250,
        bgcolor="#121212",
        border_color="#444",
        focused_border_color="#0984e3",
        text_style=ft.TextStyle(color="white", size=16),
        visible=False,
    )
    guess_button = ft.ElevatedButton(
        "Adivinhar",
        bgcolor="#0984e3",
        color="white",
        width=250,
        height=45,
        visible=False,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
    )
    result_text = ft.Text("", size=18, color="#ffeaa7", visible=False, weight="bold", text_align="center")

    score_list = ft.Column(scroll="auto", height=200)

    def load_scores():
        score_list.controls.clear()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                for line in file.readlines():
                    score_list.controls.append(styled_text(line.strip(), size=14, color="#dfe6e9"))
        page.update()

    def save_score(attempts, start, end):
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(DATA_FILE, "a", encoding="utf-8") as file:
            file.write(f"[{now}] Intervalo: {start} a {end} - Acertou em {attempts} tentativas\n")

    def start_game(e):
        nonlocal target_number, attempts, range_start, range_end
        try:
            start = int(input_range_start.value)
            end = int(input_range_end.value)
            if start >= end:
                result_text.value = "⚠️ O número inicial deve ser menor que o final."
                result_text.color = "#d63031"
                result_text.visible = True
                page.update()
                return
            range_start = start
            range_end = end
            target_number = random.randint(start, end)
            attempts = 0
            guess_input.visible = True
            guess_button.visible = True
            result_text.visible = False
            guess_input.value = ""
            page.update()
        except ValueError:
            result_text.value = "⚠️ Insira números válidos."
            result_text.color = "#d63031"
            result_text.visible = True
            page.update()

    def check_guess(e):
        nonlocal attempts
        try:
            guess_str = guess_input.value.strip()
            if guess_str == "":
                result_text.value = "⚠️ Digite um número válido."
                result_text.color = "#d63031"
                result_text.visible = True
                page.update()
                return
            
            guess = int(guess_str)
            attempts += 1

            if guess == target_number:
                result_text.value = f"🎉 Parabéns! Você acertou em {attempts} tentativas."
                result_text.color = "#00b894"
                save_score(attempts, range_start, range_end)
                load_scores()
                guess_input.visible = False
                guess_button.visible = False
            elif guess < target_number:
                result_text.value = "⬆️ Tente um número maior."
                result_text.color = "#ffeaa7"
            else:
                result_text.value = "⬇️ Tente um número menor."
                result_text.color = "#ffeaa7"

            result_text.visible = True
            guess_input.value = ""
            page.update()
        except ValueError:
            result_text.value = "⚠️ Digite um número válido."
            result_text.color = "#d63031"
            result_text.visible = True
            page.update()

    start_button.on_click = start_game
    guess_button.on_click = check_guess

    page.add(
        styled_text("🎯 Jogo de Adivinhação", size=30, weight="bold", color="#00cec9", center=True),
        input_range_start,
        input_range_end,
        start_button,
        guess_input,
        guess_button,
        result_text,
        styled_text("🏆 Histórico de Pontuações", size=20, weight="bold", color="#00cec9", center=True),
        score_list,
    )

    load_scores()

ft.app(target=main)
