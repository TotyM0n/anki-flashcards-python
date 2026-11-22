import flet as ft
from database import init_db, add_word, get_due_cards, review_word
from importer import get_word_info

BG_COLOR = "#141416"
CARD_BG = "#1F1F24"
BORDER_COLOR = "#32323A"
ACCENT_YELLOW = "#FDE047"
DARK_TEXT = "#141416"
TEXT_MAIN = "#F4F4F5"
TEXT_MUTED = "#A1A1AA"

def main(page: ft.Page):
    page.title = "Manki — Умные карточки"
    page.window.icon = "icon.png"
    page.window.width = 440
    page.window.height = 760
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BG_COLOR
    page.padding = 20

    page.theme = ft.Theme(color_scheme_seed=ACCENT_YELLOW)

    init_db()

    due_cards = []
    current_card = None
    is_translation_shown = False

    counter_text = ft.Text("", size=13, color=TEXT_MUTED, weight=ft.FontWeight.W_500)
    word_text = ft.Text(
        "Загрузка...",
        size=34,
        weight=ft.FontWeight.BOLD,
        color=TEXT_MAIN,
        text_align=ft.TextAlign.CENTER,
    )
    translation_text = ft.Text(
        "",
        size=20,
        color=ACCENT_YELLOW,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    def load_next_card():
        nonlocal due_cards, current_card, is_translation_shown
        due_cards = get_due_cards()
        is_translation_shown = False
        translation_text.value = ""
        rating_row.visible = False

        if due_cards:
            current_card = next(iter(due_cards))
            word_text.value = current_card["word"]
            counter_text.value = f"Карточек на сегодня: {len(due_cards)}"
            show_btn.visible = True
        else:
            current_card = None
            word_text.value = "На сегодня всё!"
            translation_text.value = "Отличная работа, все слова повторены."
            counter_text.value = "0 карточек в очереди"
            show_btn.visible = False
        page.update()

    def on_show_translation(e):
        nonlocal is_translation_shown
        if current_card and not is_translation_shown:
            translation_text.value = current_card["translation"]
            is_translation_shown = True
            show_btn.visible = False
            rating_row.visible = True
            page.update()

    def on_rate(rating_value: int):
        if current_card:
            review_word(current_card["id"], rating_value)
            load_next_card()

    show_btn = ft.Button(
        content=ft.Text("Показать перевод", size = 16, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
        bgcolor=ACCENT_YELLOW,
        width=260,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
        on_click=on_show_translation,
    )

    def make_rating_btn(label: str, rating_val: int, is_primary: bool = False):
        return ft.Button(
            content=ft.Text(
                label,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=DARK_TEXT if is_primary else TEXT_MAIN,
            ),
            bgcolor=ACCENT_YELLOW if is_primary else CARD_BG,
            height=46,
            expand=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                side=ft.BorderSide(1, ACCENT_YELLOW if is_primary else BORDER_COLOR),
            ),
            on_click=lambda e: on_rate(rating_val),
        )

    rating_row = ft.Row(
        controls=[
            make_rating_btn("Снова", 1),
            make_rating_btn("Трудно", 2),
            make_rating_btn("Хорошо", 3, is_primary=True),
            make_rating_btn("Легко", 4),
        ],
        spacing=8,
        visible=False,
    )

    study_view = ft.Column(
        controls=[
            counter_text,
            ft.Container(
                content=ft.Column(
                    controls=[
                        word_text,
                        ft.Divider(height=1, color=BORDER_COLOR),
                        translation_text,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                ),
                bgcolor=CARD_BG,
                border=ft.Border.all(1, BORDER_COLOR),
                border_radius=20,
                padding=28,
                width=400,
                height=280,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Container(height=10),
            show_btn,
            rating_row,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=16,
    )

    word_input = ft.TextField(
        label="Английское слово",
        hint_text="Например: serendipity",
        border_color=BORDER_COLOR,
        focused_border_color=ACCENT_YELLOW,
        cursor_color=ACCENT_YELLOW,
        border_radius=12,
        width=360,
    )
    status_text = ft.Text("", size=14, text_align=ft.TextAlign.CENTER)

    def on_import_click(e):
        raw = word_input.value.strip()
        if not raw:
            return
        status_text.value = "Загружаю перевод и транскрипцию..."
        status_text.color = ACCENT_YELLOW
        page.update()

        info = get_word_info(raw)
        full_translation = f"{info['phonetic']} — {info['translation']}" if info["phonetic"] else info["translation"]
        add_word(info["word"], full_translation)

        status_text.value = f"Сохранено: {info['word']}\n{full_translation}"
        status_text.color = TEXT_MAIN
        word_input.value = ""
        page.update()

    add_btn = ft.Button(
        content=ft.Text("Найти и добавить", size=16, weight=ft.FontWeight.BOLD, color=DARK_TEXT),
        bgcolor=ACCENT_YELLOW,
        width=260,
        height=50,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=14)),
        on_click=on_import_click,
    )

    add_view = ft.Column(
        controls=[
            ft.Text("Импорт из словаря", size=22, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
            ft.Text("Введите слово, перевод подтянется автоматически", size=13, color=TEXT_MUTED),
            ft.Container(height=8),
            word_input,
            add_btn,
            status_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        visible=False,
    )

    def on_nav_change(e):
        index = e.control.selected_index
        study_view.visible = (index == 0)
        add_view.visible = (index == 1)
        if index == 0:
            load_next_card()
        page.update()

    page.navigation_bar = ft.NavigationBar(
        bgcolor=CARD_BG,
        indicator_color=ACCENT_YELLOW,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.SCHOOL_OUTLINED,
                selected_icon=ft.Icons.SCHOOL,
                label="Учить",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                selected_icon=ft.Icons.ADD_CIRCLE,
                label="Добавить",
            ),
        ],
        on_change=on_nav_change,
    )

    header = ft.Container(
        content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Image(src="icon.png", width=42, height=42, fit=ft.BoxFit.COVER),
                        border_radius=21,
                        border=ft.Border.all(2, ACCENT_YELLOW),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    ft.Text("Manki", size=26, weight=ft.FontWeight.BOLD, color=TEXT_MAIN),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            padding=ft.Padding.only(top=4, bottom=8),
        )

    page.add(header, study_view, add_view)
    load_next_card()

ft.run(main, assets_dir="assets")