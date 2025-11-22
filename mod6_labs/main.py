# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
import datetime
import asyncio
import httpx
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.page.scroll = "auto"
        self.setup_page()
        
        # Initialize history
        self.search_history = []
        self.current_alert = None 
        
        # --- STATE TRACKING ---
        self.current_unit = "metric" # Default to metric
        self.current_temp = 0
        self.current_feels_like = 0
        self.forecast_data = None # Store forecast data for unit conversion
        
        self.build_ui()
        
        # --- AUTO-FETCH LOCATION ON START ---
        self.page.run_task(self.get_current_location_weather)

    def add_to_history(self, city: str):
        """Add city to search history and update UI."""
        city = city.strip().title()
        
        if city in self.search_history:
            self.search_history.remove(city)
            
        self.search_history.insert(0, city)
        self.search_history = self.search_history[:5]
        
        self.search_bar.controls = [
            ft.ListTile(
                title=ft.Text(c, color=ft.Colors.BLACK),
                leading=ft.Icon(ft.Icons.HISTORY, color=ft.Colors.GREY),
                on_click=lambda e, city=c: self.search_from_history(city)
            ) for c in self.search_history
        ]
        
        item_count = len(self.search_history)
        view_height = min(350, max(70, item_count * 65))
        
        self.search_bar.view_size_constraints = ft.BoxConstraints(max_height=view_height)
        self.search_bar.update()

    def search_from_history(self, city):
        """Handle click on history item."""
        self.search_bar.close_view(city)
        self.on_search(None)

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
        self.page.banner = None

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            self.weather_container.bgcolor = ft.Colors.BLUE
            
            self.search_bar.bar_bgcolor = ft.Colors.GREY_900
            self.search_bar.view_bgcolor = ft.Colors.GREY_900
            self.search_bar.bar_border_side = ft.BorderSide(1, ft.Colors.GREY_700)
            self.search_bar.bar_leading = ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.BLUE_200)
            
            if hasattr(self, 'temperature'):
                self.update_display() 
            
            if hasattr(self, 'additional_info_cards'):
                all_cards = self.additional_info_cards + getattr(self, 'forecast_cards', []) + getattr(self, 'solar_events', [])
                for card in all_cards:
                    card.bgcolor = ft.Colors.BLUE_50
                    
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
            self.weather_container.bgcolor = ft.Colors.BLUE_50
            
            self.search_bar.bar_bgcolor = ft.Colors.WHITE
            self.search_bar.view_bgcolor = ft.Colors.WHITE
            self.search_bar.bar_border_side = ft.BorderSide(1, ft.Colors.BLACK)
            self.search_bar.bar_leading = ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.BLUE_700)

            if hasattr(self, 'temperature'):
                self.update_display() 

            if hasattr(self, 'additional_info_cards'):
                all_cards = self.additional_info_cards + getattr(self, 'forecast_cards', []) + getattr(self, 'solar_events', [])
                for card in all_cards:
                    card.bgcolor = ft.Colors.WHITE
        self.page.update()

    def toggle_units(self, e):
        """Toggle between Celsius and Fahrenheit."""
        if self.current_unit == "metric":
            self.current_unit = "imperial"
            self.current_temp = (self.current_temp * 9/5) + 32
            self.current_feels_like = (self.current_feels_like * 9/5) + 32
        else:
            self.current_unit = "metric"
            self.current_temp = (self.current_temp - 32) * 5/9
            self.current_feels_like = (self.current_feels_like - 32) * 5/9
            
        self.update_display()
        self.update_forecast_display()

    def update_display(self):
        """Update temperature displays on the UI."""
        unit_sym = "°C" if self.current_unit == "metric" else "°F"
        
        self.unit_button.text = unit_sym
        self.unit_button.update()
        
        self.temperature.value = f"{self.current_temp:.1f}{unit_sym}"
        self.feelslike.value = f"Feels like {self.current_feels_like:.1f}{unit_sym}"
        
        is_hot = False
        if self.current_unit == "metric":
            is_hot = self.current_temp > 35
        else:
            is_hot = self.current_temp > 95

        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.temperature.color = ft.Colors.RED_900 if is_hot else ft.Colors.BLUE_900
            self.feelslike.color = ft.Colors.GREY_700
        else:
            self.temperature.color = ft.Colors.ORANGE_200 if is_hot else ft.Colors.BLUE_50
            self.feelslike.color = ft.Colors.GREY_200
            
        self.temperature.update()
        self.feelslike.update()

    def update_forecast_display(self):
        """Rebuild forecast cards with current unit."""
        if not self.forecast_data:
            return

        self.forecast_cards.clear()
        daily_data = [item for item in self.forecast_data['list'] if "12:00:00" in item['dt_txt']]
        
        for item in daily_data[:5]:
            f_date_str = item['dt_txt']
            f_date = datetime.datetime.strptime(f_date_str, "%Y-%m-%d %H:%M:%S")
            f_day = f_date.strftime("%a")
            
            # Get base temp (Metric)
            f_temp = item['main']['temp']
            
            # Convert if needed
            if self.current_unit == "imperial":
                f_temp = (f_temp * 9/5) + 32
                
            f_icon = item['weather'][0]['icon']
            
            card_bg = ft.Colors.WHITE if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.BLUE_50
            
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f_day, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                        ft.Image(src=f"https://openweathermap.org/img/wn/{f_icon}.png", width=50, height=50),
                        ft.Text(f"{f_temp:.0f}°", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_900),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                ),
                padding=10,
                width=80,
                bgcolor=card_bg,
                border_radius=10,
            )
            self.forecast_cards.append(card)
            
        self.forecast_row.controls = self.forecast_cards
        
        if self.forecast_row.page:
            self.forecast_row.update()

    def build_ui(self):
        """Build the user interface."""
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )

        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )
        
        self.unit_button = ft.TextButton(
            text="°C",
            icon=ft.Icons.THERMOSTAT,
            tooltip="Toggle Unit",
            on_click=self.toggle_units,
            style=ft.ButtonStyle(color=ft.Colors.BLUE_700)
        )

        title_row = ft.Row(
            [
                self.title,
                ft.Row([self.unit_button, self.theme_button]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.search_bar = ft.SearchBar(
            view_elevation=4,
            divider_color=ft.Colors.GREY_400,
            bar_hint_text="Enter city name (e.g. London)",
            view_hint_text="Recent searches...",
            on_submit=self.on_search,
            on_tap=lambda e: self.search_bar.open_view(),
            
            bar_bgcolor=ft.Colors.WHITE,
            bar_shape=ft.RoundedRectangleBorder(radius=5),
            bar_border_side=ft.BorderSide(width=1, color=ft.Colors.BLACK),
            bar_leading=ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.BLUE_700),
            bar_elevation=0,
            
            view_bgcolor=ft.Colors.WHITE,
            view_shape=ft.RoundedRectangleBorder(radius=5),
            view_size_constraints=ft.BoxConstraints(max_height=70),
            
            controls=[] 
        )
        
        # --- LOCATION BUTTON ---
        self.location_button = ft.IconButton(
            icon=ft.Icons.MY_LOCATION,
            tooltip="Use Current Location",
            on_click=lambda e: self.page.run_task(self.get_current_location_weather),
            icon_color=ft.Colors.BLUE_700
        )
        
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
        
        search_row = ft.Row(
            [
                ft.Container(self.search_bar, expand=True),
                self.location_button, 
                self.search_button, 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )
        
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        self.error_message = ft.Text("", color=ft.Colors.RED_700, visible=False)
        self.loading = ft.ProgressRing(visible=False)
        
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
            self.page.close(self.current_alert)
            self.current_alert = None

    async def get_current_location_weather(self):
        """Get weather for current location using IP."""
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://ipapi.co/json/")
                data = response.json()
                city = data.get('city', '')
                
                if city:
                    self.search_bar.value = city
                    self.search_bar.update()
                    await self.get_weather()
                else:
                    self.show_error("Could not detect your city name.")
                    self.loading.visible = False
                    self.page.update()
                    
        except Exception as e:
            self.show_error("Could not detect your location. Check internet connection.")
            self.loading.visible = False
            self.page.update()

    def on_search(self, e):
        """Handle search button click or enter key press."""
        if self.current_alert:
            self.close_banner()

        current_val = self.search_bar.value
        if current_val:
            self.search_bar.close_view(current_val)
        self.page.run_task(self.get_weather)

    # --- NEW: WARNING SYSTEM LOGIC ---
    def get_weather_warnings(self, data: dict):
        """Analyze weather data and return a warning message and style."""
        
        temp = data.get("main", {}).get("temp", 0)
        wind = data.get("wind", {}).get("speed", 0)
        weather_desc = data.get("weather", [{}])[0].get("main", "").lower()
        
        warning = None
        
        # 1. Extreme Heat
        if temp > 35:
            warning = {
                "msg": f"Extreme Heat Alert! ({temp:.1f}°C)\nWear sunscreen and stay hydrated.",
                "color": ft.Colors.RED_100,
                "icon": ft.Icons.HEAT_PUMP,
                "icon_color": ft.Colors.RED
            }
        # 2. High Heat (Warning Level)
        elif temp > 30:
            warning = {
                "msg": f"High Temperature Warning ({temp:.1f}°C)\nLimit outdoor activities.",
                "color": ft.Colors.AMBER_100,
                "icon": ft.Icons.WARNING,
                "icon_color": ft.Colors.AMBER
            }
        # 3. Extreme Cold
        elif temp < 5:
            warning = {
                "msg": f"Freeze Warning! ({temp:.1f}°C)\nWear heavy winter clothing.",
                "color": ft.Colors.BLUE_100,
                "icon": ft.Icons.AC_UNIT,
                "icon_color": ft.Colors.BLUE
            }
        # 4. High Wind
        elif wind > 15: # m/s
            warning = {
                "msg": f"High Wind Alert! ({wind} m/s)\nSecure loose objects outside.",
                "color": ft.Colors.GREY_300,
                "icon": ft.Icons.AIR,
                "icon_color": ft.Colors.GREY_700
            }
        # 5. Rain/Storm
        elif "rain" in weather_desc or "storm" in weather_desc:
            warning = {
                "msg": "Rain/Storm Detected.\nDon't forget your umbrella!",
                "color": ft.Colors.BLUE_GREY_100,
                "icon": ft.Icons.UMBRELLA,
                "icon_color": ft.Colors.BLUE_GREY_700
            }
            
        return warning

    async def display_weather(self, data: dict, forecast_data: dict = None):
        """Display weather information."""
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        
        self.current_unit = "metric"
        self.current_temp = data.get("main", {}).get("temp", 0)
        self.current_feels_like = data.get("main", {}).get("feels_like", 0)
        self.forecast_data = forecast_data 
        
        self.unit_button.text = "°C"
        self.unit_button.update()
        
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

        self.forecast_cards = []
        self.forecast_row = ft.Row(
            self.forecast_cards, 
            scroll="adaptive", 
            alignment=ft.MainAxisAlignment.SPACE_EVENLY
        )
        self.update_forecast_display() 

        self.temperature = ft.Text(
            f"{self.current_temp:.1f}°C",
            size=48,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_900 if self.current_temp <= 35 else ft.Colors.RED_900,
        )
        
        self.feelslike = ft.Text(
            f"Feels like {self.current_feels_like:.1f}°C", 
            size=16, 
            color=ft.Colors.GREY_700
        )
        
        self.description = ft.Text(description, size=16, italic=True, color=ft.Colors.GREY_700)

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
                self.forecast_row,
                ft.Text(f"As of {date_display}", size=12, italic=True)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        # --- NEW: INTEGRATED ALERT SYSTEM ---
        warning = self.get_weather_warnings(data)
        if warning:
            self.current_alert = ft.Banner(
                bgcolor=warning["color"],
                leading=ft.Icon(warning["icon"], color=warning["icon_color"], size=40),
                content=ft.Text(warning["msg"], color=ft.Colors.BLACK),
                actions=[
                    ft.TextButton("Dismiss", on_click=self.close_banner)
                ],
            )
            self.page.open(self.current_alert)

        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.error_message.visible = False
        self.page.update()

    async def get_weather(self):
        """Fetch and display weather data."""
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