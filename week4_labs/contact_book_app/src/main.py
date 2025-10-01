 # main.py
import flet as ft 
from database import init_db 
from app_logic import display_contacts, add_contact, clear_error
 
def main(page: ft.Page): 
    page.title = "Contact Book" 
    page.vertical_alignment = ft.MainAxisAlignment.START 
    page.window.width = 1080 
    page.window.min_width = 600
    page.window.height = 900
    page.window.min_height = 900
    page.theme_mode = ft.ThemeMode.LIGHT

    def change_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    theme_switch = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        icon_color=ft.Colors.ORANGE_ACCENT,
        on_click=change_theme
    )

    db_conn = init_db() 
 
    name_input = ft.TextField(icon=ft.Icon(name="PERSON", color=ft.Colors.DEEP_ORANGE), label="Name", width=350, on_change=lambda e: clear_error(page, e)) 
    phone_input = ft.TextField(icon=ft.Icon(name="PHONE", color=ft.Colors.DEEP_ORANGE), label="Phone", width=350, on_change=lambda e: clear_error(page, e)) 
    email_input = ft.TextField(icon=ft.Icon(name="EMAIL", color=ft.Colors.DEEP_ORANGE), label="Email", width=350, on_change=lambda e: clear_error(page, e)) 
    search_input = ft.TextField(icon=ft.Icon(name="SEARCH", color=ft.Colors.DEEP_ORANGE), label="Search Contact", width=400, height=45, border_radius=ft.border_radius.all(50), on_change=lambda e: display_contacts(page, contacts_list_view, search_input, db_conn))

    inputs = (name_input, phone_input, email_input) 
 
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True, height=350) 
 
    add_button = ft.ElevatedButton( 
        text="Add Contact", 
        color=ft.Colors.DEEP_ORANGE_ACCENT,
        width=350,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, search_input, db_conn) 
    ) 

    page.add( 
        ft.Column( 
            [   
            ft.Row(
                [
                ft.Text("Contact Book App", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER,), 
                theme_switch
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            ),
                ft.Column(
                    [
                        ft.Text("Enter Contact Details:", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), 
                        ft.Container(
                            content=ft.Column(
                                [name_input, phone_input, email_input, add_button]
                            ),
                            border=ft.border.all(1, ft.Colors.GREY_500),
                            padding=ft.padding.all(20),
                            border_radius=ft.border_radius.all(10),
                        ),
                        ft.Divider(), 
                        ft.Row(
                            [
                            ft.Text("Contacts:", size=24, weight=ft.FontWeight.BOLD), 
                            search_input,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        contacts_list_view, 
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    expand=True
                )
            ]
        )
    ) 
 
    display_contacts(page, contacts_list_view, search_input, db_conn) 
 
if __name__ == "__main__": 
    ft.app(target=main)