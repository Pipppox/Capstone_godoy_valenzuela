import flet as ft

ft.Text("Flet is fun to build with!", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)

ft.Row(
    alignment=ft.MainAxisAlignment.CENTER,
    controls=[
        ft.Icon(ft.Icons.STAR),
        ft.Text("Featured"),
    ],
)



