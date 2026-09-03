import flet as ft
from views.login_view import login_view

def main(page: ft.Page):
    page.title = "Stockin - Login"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    page.padding = 0

    page.add(login_view(page))

if __name__ == "__main__":
    ft.run(main)