import flet as ft
import mysql.connector
from db_connection import connect_db

def main(page: ft.Page):
    # set up window config and app style
    page.title = "Login"
    page.window.title_bar_hidden = True
    page.window.alignment = ft.Alignment(0.0, 0.0)
    page.window.frameless = True
    page.window.width = 400
    page.window.height = 350
    page.bgcolor = ft.Colors.AMBER_ACCENT
    page.theme_mode = ft.ThemeMode.LIGHT

    def login_click(e):
        # when login button is clicked, will process login
        print("Login button clicked")

        usernameval = username.value
        passwordval = password.value

        success_dialog = ft.AlertDialog(
            icon=ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=50),
            title=ft.Text("Login Successful", text_align=ft.TextAlign.CENTER),
            content=ft.Text(f'Welcome, {usernameval}!', text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(success_dialog))],
        )
        failure_dialog = ft.AlertDialog(
            icon=ft.Icon(name=ft.Icons.ERROR, color=ft.Colors.RED, size=50),
            title=ft.Text("Login Failed"),
            content=ft.Text("Invalid username or password."),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(failure_dialog))],
        )
        invalid_input_dialog = ft.AlertDialog(
            icon=ft.Icon(name=ft.Icons.INFO, color=ft.Colors.BLUE, size=50),
            title=ft.Text("Input Error", text_align=ft.TextAlign.CENTER),
            content=ft.Text("Please enter username and password.", text_align=ft.TextAlign.CENTER),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(invalid_input_dialog))],
        )
        database_error_dialog = ft.AlertDialog(
            title=ft.Text("Database Error"),
            content=ft.Text("An error occurred while connecting to the database."),
            actions=[ft.TextButton("OK", on_click=lambda e: page.close(database_error_dialog))],
        )

        # check if inputs arent empty
        if not usernameval or not passwordval:
            page.open(invalid_input_dialog)
            return
        
        try:
            # try to connect to db and check usr credentials
            conn = connect_db()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (usernameval, passwordval))
            user = cursor.fetchone()

            if user:
                page.open(success_dialog)
            else:
                page.open(failure_dialog)

            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            # print error if issue connect to db and show error dialog 
            print(f"Database error: {err}")
            page.open(database_error_dialog)
            page.update()

    # define the UI components 
    title = ft.Text(
            "User Login", 
            size=20, 
            weight=ft.FontWeight.BOLD,
            font_family="Arial", 
            text_align=ft.TextAlign.RIGHT, 
            color=ft.Colors.BLACK
        )
    username = ft.TextField(
            label="User name", 
            width=300,
            hint_text="Enter your user name",
            helper_text="This is your unique identifier",
            autofocus=True,
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
            icon=ft.Icons.PERSON
        )
    password = ft.TextField(
            label="Password", 
            hint_text="Enter your password",
            helper_text="This is your secret key",
            bgcolor=ft.Colors.LIGHT_BLUE_ACCENT,
            password=True, 
            can_reveal_password=True, 
            width=300,
            icon=ft.Icons.PASSWORD
        )
    login_btn = ft.ElevatedButton(
            text="Login",
            width=100,
            icon=ft.Icons.LOGIN,
            on_click=login_click
        )

    # add all components to main page layout
    page.add(
        ft.Container(
            content=ft.Column(
                [title, 
                 username, 
                 password,
                 ft.Container(
                    login_btn,
                    alignment=ft.alignment.top_right,
                    margin=ft.margin.only(0,20,40,0)
                 )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            expand=True,
            alignment=ft.alignment.center
        ),
    )

ft.app(target=main)
