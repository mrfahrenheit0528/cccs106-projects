# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
import datetime
import asyncio
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.page.scroll = "auto"
        self.setup_page()
        
        # Initialize history before building UI
        self.search_history = []
        self.current_alert = None # Track the active alert
        
        self.build_ui()

    def add_to_history(self, city: str):
        """Add city to search history and update UI."""
        # Clean up the city name (Title Case)
        city = city.strip().title()
        
        # Remove if exists (to move it to top)
        if city in self.search_history:
            self.search_history.remove(city)
            
        # Add to top
        self.search_history.insert(0, city)
        self.search_history = self.search_history[:5]  # Keep last 5
        
        # Update the SearchBar controls (The view content)
        self.search_bar.controls = [
            ft.ListTile(
                title=ft.Text(c),
                leading=ft.Icon(ft.Icons.HISTORY),
                on_click=lambda e, city=c: self.search_from_history(city)
            ) for c in self.search_history
        ]
        
        # --- DYNAMIC HEIGHT ADJUSTMENT ---
        item_count = len(self.search_history)
        view_height = min(350, max(70, item_count * 65))
        
        # Corrected property for size constraints
        self.search_bar.view_size_constraints = ft.BoxConstraints(max_height=view_height)
        self.search_bar.update()

    def search_from_history(self, city):
        """Handle click on history item."""
        self.search_bar.close_view(city) # Closes view and sets text to city
        self.on_search(None) # Trigger search

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
        self.page.padding = 20
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
            
            # Update SearchBar style for Dark Mode
            self.search_bar.bar_bgcolor = ft.Colors.GREY_900
            self.search_bar.view_bgcolor = ft.Colors.GREY_900
            self.search_bar.bar_border_side = ft.BorderSide(1, ft.Colors.GREY_700)
            self.search_bar.bar_leading = ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.BLUE_200)
            
            if hasattr(self, 'additional_info_cards'):
                all_cards = self.additional_info_cards + getattr(self, 'forecast_cards', []) + getattr(self, 'solar_events', [])
                for card in all_cards:
                    card.bgcolor = ft.Colors.BLUE_50
            
            if hasattr(self, 'temp'):
                if self.temp <= 35:
                    self.temperature.color = ft.Colors.BLUE_50
                else:
                    self.temperature.color = ft.Colors.ORANGE_200
            
            if hasattr(self, 'feelslike'):
                self.feelslike.color = ft.Colors.GREY_200
                self.description.color = ft.Colors.GREY_100
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.weather_container.bgcolor = ft.Colors.BLUE_50
            
            # Update SearchBar style for Light Mode
            self.search_bar.bar_bgcolor = ft.Colors.WHITE
            self.search_bar.view_bgcolor = ft.Colors.WHITE
            self.search_bar.bar_border_side = ft.BorderSide(1, ft.Colors.BLACK)
            self.search_bar.bar_leading = ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.BLUE_700)

            if hasattr(self, 'additional_info_cards'):
                all_cards = self.additional_info_cards + getattr(self, 'forecast_cards', []) + getattr(self, 'solar_events', [])
                for card in all_cards:
                    card.bgcolor = ft.Colors.WHITE
            
            if hasattr(self, 'temp'):
                if self.temp <= 35:
                    self.temperature.color = ft.Colors.BLUE_900
                else:
                    self.temperature.color = ft.Colors.RED_900
            
            if hasattr(self, 'feelslike'):
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

        # Theme toggle
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        title_row = ft.Row(
            [self.title, self.theme_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        # --- CUSTOM STYLED SEARCH BAR ---
        
        self.search_bar = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.Colors.GREY_400,
            bar_hint_text="Enter city name (e.g. London)",
            view_hint_text="Recent searches...",
            on_submit=self.on_search,
            
            on_tap=lambda e: self.search_bar.open_view(),
            
            # --- DESIGN ---
            bar_bgcolor=ft.Colors.WHITE,
            bar_shape=ft.RoundedRectangleBorder(radius=5),
            bar_border_side=ft.BorderSide(width=1, color=ft.Colors.BLACK),
            bar_leading=ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.BLUE_700),
            bar_elevation=0,
            
            # --- VIEW STYLING ---
            view_shape=ft.RoundedRectangleBorder(radius=5),
            
            # Corrected property for size constraints
            view_size_constraints=ft.BoxConstraints(max_height=70),
            
            controls=[] 
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
                shape=ft.RoundedRectangleBorder(radius=5),
                padding=20
            ),
        )
        
        # Search Layout
        search_row = ft.Row(
            [
                ft.Container(self.search_bar, expand=True), 
                self.search_button, 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        # Weather container
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text("", color=ft.Colors.RED_700, visible=False)
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Add components
        self.page.add(
            ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    search_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

    def close_banner(self, e=None):
        """Close the banner."""
        if self.current_alert:
            # Use modern close() method
            self.page.close(self.current_alert)
            self.current_alert = None

    def on_search(self, e):
        """Handle search button click or enter key press."""
        # Clear any old alerts
        if self.current_alert:
            self.close_banner()

        # Close the search view if open
        current_val = self.search_bar.value
        if current_val:
            self.search_bar.close_view(current_val)
        self.page.run_task(self.get_weather)

    async def display_weather(self, data: dict, forecast_data: dict = None):
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
        
        timezone_offset = data.get("timezone", 0)
        sunrise = datetime.datetime.utcfromtimestamp(data.get("sys", {}).get("sunrise", 0) + timezone_offset).strftime("%I:%M %p")
        sunset = datetime.datetime.utcfromtimestamp(data.get("sys", {}).get("sunset", 0) + timezone_offset).strftime("%I:%M %p")
        date_display = datetime.datetime.utcfromtimestamp(data.get("dt", 0) + timezone_offset)
        
        # Info Cards
        self.additional_info_cards = [
            self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f'{humidity}%' if humidity != 0 else 'No Data'),
            self.create_info_card(ft.Icons.AIR, "Wind Speed", f'{wind_speed} m/s' if wind_speed != 0 else 'No Data'),
            self.create_info_card(ft.Icons.WIND_POWER, "Gustiness", f'{wind_gust} m/s' if wind_gust != 0 else 'No Data'),
            self.create_info_card(ft.Icons.GAS_METER, "Pressure", f'{pressure} hPa' if pressure != 0 else 'No Data'),
        ]
        
        self.solar_events = [
            self.create_info_card(ft.Icons.SUNNY, "Sunrise", f'{sunrise}' if sunrise != 0 else 'No Data'),
            self.create_info_card(ft.Icons.SUNNY, "Sunset", f'{sunset}' if sunset != 0 else 'No Data')
        ]

        # Forecast Cards
        self.forecast_cards = []
        if forecast_data:
            daily_data = [item for item in forecast_data['list'] if "12:00:00" in item['dt_txt']]
            for item in daily_data[:5]:
                f_date_str = item['dt_txt']
                f_date = datetime.datetime.strptime(f_date_str, "%Y-%m-%d %H:%M:%S")
                f_day = f_date.strftime("%a")
                f_temp = item['main']['temp']
                f_icon = item['weather'][0]['icon']
                
                card = ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f_day, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                            ft.Image(src=f"https://openweathermap.org/img/wn/{f_icon}.png", width=50, height=50),
                            ft.Text(f"{f_temp:.0f}°C", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    padding=10,
                    width=80,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                )
                self.forecast_cards.append(card)

        # Main Text components
        self.temperature = ft.Text(
            f"{self.temp:.1f}°C",
            size=48,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_900 if self.temp <= 35 else ft.Colors.RED_900,
        )
        
        self.feelslike = ft.Text(f"Feels like {feels_like:.1f}°C", size=16, color=ft.Colors.GREY_700)
        self.description = ft.Text(description, size=16, italic=True, color=ft.Colors.GREY_700)

        # Assemble UI
        self.weather_container.content = ft.Column(
            [
                ft.Row([ft.Text(f"{city_name}, {country}", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(
                    [
                        ft.Column([self.temperature, self.feelslike]),
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Image(src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png", width=120, height=120),
                                    margin=ft.Margin(0, -11, 0, 0)
                                ),
                                self.description,
                            ],
                            spacing=-20,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                ft.Row(self.additional_info_cards, scroll="adaptive", alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Divider(),
                ft.Text("Sunrise and Sunset", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Row(self.solar_events, alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Divider(),
                ft.Text("5-Day Forecast", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Row(self.forecast_cards, scroll="adaptive", alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Text(f"As of {date_display}", size=12, italic=True)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        # Fade In Animation
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        # --- DEBUGGING LOGS ---
        print(f"DEBUG: Current Temp from API: {self.temp}")
        
        # --- WEATHER ALERTS (Modern Implementation) ---
        if self.temp > 35:
            print("DEBUG: Triggering Alert...")
            self.current_alert = ft.Banner(
                bgcolor=ft.Colors.AMBER_100,
                leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.AMBER, size=40),
                content=ft.Text(f"High temperature alert! ({self.temp:.1f}°C)", color=ft.Colors.AMBER_900, size=16),
                actions=[
                    ft.TextButton("Dismiss", on_click=self.close_banner)
                ],
            )
            # Use open() instead of assigning to property
            self.page.open(self.current_alert)

        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.error_message.visible = False
        self.page.update()

    async def get_weather(self):
        """Fetch and display weather data."""
        # Get value from SearchBar
        city = self.search_bar.value.strip() if self.search_bar.value else ""
        
        if not city:
            self.show_error("Please enter a city name")
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            weather_data, forecast_data = await asyncio.gather(
                self.weather_service.get_weather(city),
                self.weather_service.get_forecast(city)
            )
            
            await self.display_weather(weather_data, forecast_data)
            
            # Add to history after successful fetch
            self.add_to_history(city)
            
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
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
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