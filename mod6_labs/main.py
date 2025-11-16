# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
import datetime
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.page.scroll = "auto"
        self.setup_page()
        self.build_ui()

        self.search_history = []
        # self.additional_info_cards = []
    
    def add_to_history(self, city: str):
        """Add city to search history."""
        if city not in self.search_history:
            self.search_history.insert(0, city)
            self.search_history = self.search_history[:5]  # Keep last 5
    
    def build_history_dropdown(self):
        """Build dropdown with search history."""
        return ft.Dropdown(
            label="Recent Searches",
            options=[ft.dropdown.Option(city) for city in self.search_history],
            on_change=lambda e: self.load_from_history(e.control.value),
        )

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        
        # Add theme switcher
        self.page.theme_mode = ft.ThemeMode.LIGHT  # Use system theme
        
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 20
        
        # Window properties are accessed via page.window object in Flet 0.28.3
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()

    
    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            self.weather_container.bgcolor = ft.Colors.BLUE
            for card in self.additional_info_cards + self.forecast_cards + self.solar_events:
                card.bgcolor = ft.Colors.BLUE_50
            if self.temp <= 35:
                self.temperature.color = ft.Colors.BLUE_50
            else:
                self.temperature.color = ft.Colors.ORANGE_200
            self.feelslike.color = ft.Colors.GREY_200
            self.description.color = ft.Colors.GREY_100
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.weather_container.bgcolor = ft.Colors.BLUE_50
            for card in self.additional_info_cards + self.forecast_cards + self.solar_events:
                card.bgcolor = ft.Colors.WHITE
            if self.temp <= 35:
                self.temperature.color = ft.Colors.BLUE_900
            else:
                self.temperature.color = ft.Colors.RED_900
            self.feelslike.color = ft.Colors.GREY_700
            self.description.color = ft.Colors.GREY_700
        self.page.update()

    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )

        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Update the Column to include the theme button in the title row
        title_row = ft.Row(
            [
                self.title,
                self.theme_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    self.search_button,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

    
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)

    
    async def display_weather(self, data: dict):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        self.temp = data.get("main", {}).get("temp", 0)
        feels_like = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        wind_gust = data.get("wind", {}).get("gust", 0)
        sunrise = datetime.datetime.utcfromtimestamp(data.get("sys", {}).get("sunrise", 0) + data.get("timezone", 28800)).strftime("%I:%M %p")
        sunset = datetime.datetime.utcfromtimestamp(data.get("sys", {}).get("sunset", 0) + data.get("timezone", 28800)).strftime("%I:%M %p")
        date = datetime.datetime.utcfromtimestamp(data.get("dt", 0) + data.get("timezone", 28800))
        
        self.additional_info_cards = [
                self.create_info_card(
                    ft.Icons.WATER_DROP,
                    "Humidity",
                    f'{humidity}%' if humidity != 0 else 'No Data'
                ),
                self.create_info_card(
                    ft.Icons.AIR,
                    "Wind Speed",
                    f'{wind_speed} m/s' if wind_speed != 0 else 'No Data'
                ),
                self.create_info_card(
                    ft.Icons.WIND_POWER,
                    "Gustiness",
                    f'{wind_gust} m/s' if wind_gust != 0 else 'No Data'
                ),
                self.create_info_card(
                    ft.Icons.GAS_METER,
                    "Pressure",
                    f'{pressure} hPa' if pressure != 0 else 'No Data'
                ),
            ]
        self.solar_events = [
                self.create_info_card(
                    ft.Icons.SUNNY,
                    "Sunrise",
                    f'{sunrise}' if sunrise != 0 else 'No Data'
                ),
                self.create_info_card(
                    ft.Icons.SUNNY,
                    "Sunset",
                    f'{sunset}' if sunset != 0 else 'No Data'
                )
        ]
        self.forecast_cards = [
                self.create_info_card(
                    ft.Icons.ONE_K,
                    "Humidity",
                    f"{humidity if humidity != 0 else "No Data"}%"
                ),
                self.create_info_card(
                    ft.Icons.AIR,
                    "Wind Speed",
                    f"{f'{wind_speed} m/s' if wind_speed != 0 else 'No Data'}"
                ),
                self.create_info_card(
                    ft.Icons.GAS_METER,
                    "Pressure",
                    f"{pressure} hPa"
                ),
                self.create_info_card(
                    ft.Icons.GAS_METER,
                    "Pressure",
                    f"{pressure} hPa"
                ),
                self.create_info_card(
                    ft.Icons.GAS_METER,
                    "Pressure",
                    f"{pressure} hPa"
                )
            ]

        
        self.temperature = ft.Text(
                    f"{self.temp:.1f}°C",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900 if self.temp <= 35 else ft.Colors.RED_900,
                )
        
        self.feelslike =  ft.Text(
                    f"Feels like {feels_like:.1f}°C",
                    size=16,
                    color=ft.Colors.GREY_700,
                )
        self.description = ft.Text(
                            description,
                            size=16,
                            italic=True,
                            color=ft.Colors.GREY_700
                        )
        #==========================================
        # Build weather display
        #==========================================
        self.weather_container.content = ft.Column(
            [
                ft.Row(
                    [# Location
                        ft.Text(
                            f"{city_name}, {country}",
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK

                        )       
                    ],
                    alignment=ft.MainAxisAlignment.CENTER

                ),
                ft.Row(
                    [
                        ft.Column(
                            [# Temperature
                                self.temperature,
                                self.feelslike,
                            ],
                            # spacing=-9,
                        ),
                        ft.Column(
                            [# Weather icon and description
                                ft.Container(
                                    content = ft.Image(
                                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                                            width=120,
                                            height=120,
                                            ),
                                    margin=ft.Margin(0, -11, 0, 0)
                                )
                                ,
                                self.description,
                            ],
                            spacing=-20,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    # wrap=True,
                ),
                
                # Additional info
                ft.Row(
                    self.additional_info_cards,
                    scroll="adaptive",
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    # wrap=True
                ),
                ft.Divider(),
                ft.Text(
                    f"Sunrise and Sunset",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK
                ),
                ft.Row(
                    self.solar_events,
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,  
                ),
                ft.Divider(),
                ft.Text(
                    f"5-day forecas",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK
                ),
                # 5-day forecast (placeholder)
                ft.Row(
                    self.forecast_cards,
                    scroll="adaptive",
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    # wrap=True
                ),
                
                # As-of date
                ft.Text(
                    f"As of {date}",
                    size=12,
                    italic=True,

                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        # In display_weather method, add animation to container
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        # Fade in
        import asyncio
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        
        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()

    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Display weather
            await self.display_weather(weather_data)
            
        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()
    
    
 
def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)