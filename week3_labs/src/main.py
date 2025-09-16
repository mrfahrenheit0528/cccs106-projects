import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    page.title = "Login"
    page.window.title_bar_hidden = True
    page.window.alignment = ft.Alignment(0.0, 0.0)
    page.window.frameless = True
    page.window.width = 400
    page.window.height = 350
    page.bgcolor = ft.Colors.AMBER_ACCENT

    # Create your login form
    title = ft.Text("User Login", theme_style=ft.TextThemeStyle.DISPLAY_LARGE, font_family="Century Gothic", text_align=ft.TextAlign.RIGHT, color=ft.Colors.BLACK87)
    username = ft.TextField(label="Username", width=400)
    password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=400)
    login_btn = ft.ElevatedButton(text="Login")

    # Wrap in a container that fills the page and centers content
    page.add(
        ft.Container(
            content=ft.Column(
                [title, username, password, login_btn],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            expand=True,
            alignment=ft.alignment.center
        )
    )

ft.app(target=main)
