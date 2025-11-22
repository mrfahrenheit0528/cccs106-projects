"""Weather Application using Flet v0.28.3"""

import flet as ft
import datetime
import asyncio
import httpx
from weather_service import WeatherService
from ai_service import AIService
from config import Config


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.ai_service = AIService()
        self.page.scroll = "auto"
        self.setup_page()
        
        # Initialize history
        self.search_history = []
        self.current_alert = None 
        
        # --- Restore Cache Initialization ---
        self.weather_cache = {} 
        # Duration for which weather data is cached (in minutes)
        self.CACHE_DURATION = datetime.timedelta(minutes=10)
        
        # --- STATE TRACKING ---
        self.current_unit = "metric" # Default to metric
        self.current_temp = 0
        self.current_feels_like = 0
        self.forecast_data = None 
        self.build_ui()
        self.page.update()
        
        # --- AUTO-FETCH LOCATION ON START ---
        self.page.run_task(self.get_current_location_weather)
        self.page.run_task(self.get_current_location_weather)

    def add_to_history(self, city: str):
        """Add city to search history and update UI."""
        city = city.strip().title()
        
        if city in self.search_history:
            self.search_history.remove(city)
        
        self.search_history.insert(0, city)
        self.search_history = self.search_history[:5]
        
        # Determine text color based on current theme
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        text_color = ft.Colors.WHITE if is_dark else ft.Colors.BLACK
        icon_color = ft.Colors.GREY_400 if is_dark else ft.Colors.GREY

        self.search_bar.controls = [
            ft.ListTile(
                title=ft.Text(c, color=text_color),
                leading=ft.Icon(ft.Icons.HISTORY, color=icon_color),
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
        self.search_bar.value = city
        self.on_search(None)

    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # --- NEW COLOR SCHEME ---
        self.page.theme = ft.Theme(color_scheme_seed="#3182CE") 
        self.page.dark_theme = ft.Theme(color_scheme_seed="#63B3ED")
        
        self.page.bgcolor = "#F0F4F8" # Light mode background
        
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()
        self.page.banner = None

    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            # SWITCH TO DARK
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
            
            self.page.bgcolor = "#1A202C"
            container_bg = "#2D3748"
            text_color = "#F7FAFC"
            sub_text_color = "#A0AEC0"
            input_bg = "#2D3748"
            input_color = "#F7FAFC"
            
        else:
            # SWITCH TO LIGHT
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE

            self.page.bgcolor = "#F0F4F8"
            container_bg = "#FFFFFF"
            text_color = "#1A202C"
            sub_text_color = "#718096"
            input_bg = "#FFFFFF"
            input_color = "#1A202C"

        # Apply Colors to Components
        self.weather_container.bgcolor = container_bg
        
        self.search_bar.bar_bgcolor = input_bg
        self.search_bar.text_style = ft.TextStyle(color=input_color)
        self.search_bar.view_bgcolor = input_bg
        self.search_bar.bar_border_side = ft.BorderSide(1, sub_text_color)
        self.search_bar.bar_leading = ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.PRIMARY)
        # Update history list tile colors if they exist
        if self.search_history:
             self.search_bar.controls = [
                ft.ListTile(
                    title=ft.Text(c, color=text_color),
                    leading=ft.Icon(ft.Icons.HISTORY, color=sub_text_color),
                    on_click=lambda e, city=c: self.search_from_history(city)
                ) for c in self.search_history
            ]

        # Update display
        if hasattr(self, 'temperature'):
            self.update_display() 
            
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
        if not hasattr(self, 'temperature'):
            return

        unit_sym = "°C" if self.current_unit == "metric" else "°F"
        
        self.unit_button.text = unit_sym
        self.unit_button.update()
        
        self.temperature.value = f"{self.current_temp:.1f}{unit_sym}"
        self.feelslike.value = f"Feels like {self.current_feels_like:.1f}{unit_sym}"
        
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        primary_col = "#F7FAFC" if is_dark else "#1A202C"
        secondary_col = "#A0AEC0" if is_dark else "#718096"
        card_bg = "#2D3748" if is_dark else "#FFFFFF"
        
        # Temperature Color Logic
        is_hot = False
        if self.current_unit == "metric":
            is_hot = self.current_temp > 35
        else:
            is_hot = self.current_temp > 95

        if is_hot:
            temp_col = ft.Colors.ORANGE_300 if is_dark else ft.Colors.RED_600
        else:
            temp_col = primary_col

        self.temperature.color = temp_col
        self.feelslike.color = secondary_col
        self.description.color = secondary_col
        self.location_text.color = primary_col
        self.solar_title.color = primary_col
        self.forecast_title.color = primary_col
        
        # REBUILD CARDS TO UPDATE COLORS
        
        # 1. Additional Info
        if hasattr(self, 'last_weather_data'):
             humidity = self.last_weather_data.get("main", {}).get("humidity", 0)
             wind_speed = self.last_weather_data.get("wind", {}).get("speed", 0)
             pressure = self.last_weather_data.get("main", {}).get("pressure", 0)
             wind_gust = self.last_weather_data.get("wind", {}).get("gust", 0)
             
             self.additional_info_row.controls = [
                self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f'{humidity}%', card_bg, primary_col, secondary_col),
                self.create_info_card(ft.Icons.AIR, "Wind Speed", f'{wind_speed} m/s', card_bg, primary_col, secondary_col),
                self.create_info_card(ft.Icons.WIND_POWER, "Gustiness", f'{wind_gust} m/s', card_bg, primary_col, secondary_col),
                self.create_info_card(ft.Icons.GAS_METER, "Pressure", f'{pressure} hPa', card_bg, primary_col, secondary_col),
            ]
             self.additional_info_row.update()

        # 2. Solar Events
        if hasattr(self, 'last_weather_data'):
             timezone_offset = self.last_weather_data.get("timezone", 0)
             sunrise = datetime.datetime.utcfromtimestamp(self.last_weather_data.get("sys", {}).get("sunrise", 0) + timezone_offset).strftime("%I:%M %p")
             sunset = datetime.datetime.utcfromtimestamp(self.last_weather_data.get("sys", {}).get("sunset", 0) + timezone_offset).strftime("%I:%M %p")
             
             self.solar_row.controls = [
                self.create_info_card(ft.Icons.SUNNY, "Sunrise", f'{sunrise}', card_bg, primary_col, secondary_col),
                self.create_info_card(ft.Icons.SUNNY, "Sunset", f'{sunset}', card_bg, primary_col, secondary_col)
            ]
             self.solar_row.update()

        # 3. Lifestyle Cards (If data exists)
        if hasattr(self, 'last_lifestyle_data'):
             ls = self.last_lifestyle_data
             # Update Trivia
             self.trivia_card.content.controls[0].controls[0].color = primary_col # Icon
             self.trivia_card.content.controls[0].controls[1].color = primary_col # Title
             self.trivia_card.content.controls[1].color = secondary_col # Text
             self.trivia_card.update()
             
             # Update Music
             self.music_card.content.controls[0].controls[0].color = primary_col 
             self.music_card.content.controls[0].controls[1].color = primary_col
             self.music_card.content.controls[1].color = secondary_col
             self.music_card.content.controls[2].color = secondary_col
             self.music_card.update()

        self.temperature.update()
        self.feelslike.update()
        self.description.update()
        self.location_text.update()
        self.solar_title.update()
        self.forecast_title.update()
        
        # Re-run forecast update for colors
        self.update_forecast_display()

    def update_forecast_display(self):
        """Rebuild forecast cards with current unit."""
        if not self.forecast_data:
            return

        self.forecast_cards.clear()
        daily_data = [item for item in self.forecast_data['list'] if "12:00:00" in item['dt_txt']]
        
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        card_bg = "#2D3748" if is_dark else "#FFFFFF"
        text_col = "#F7FAFC" if is_dark else "#1A202C"
        sub_col = "#A0AEC0" if is_dark else "#718096"
        
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
            
            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(f_day, weight=ft.FontWeight.BOLD, color=sub_col),
                        ft.Image(src=f"https://openweathermap.org/img/wn/{f_icon}.png", width=50, height=50),
                        ft.Text(f"{f_temp:.0f}°", weight=ft.FontWeight.BOLD, color=text_col),
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
        
        # ONLY UPDATE IF ADDED TO PAGE
        if self.forecast_row.page:
            self.forecast_row.update()

    def build_ui(self):
        """Build the user interface."""
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.PRIMARY, # Uses theme color
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
            style=ft.ButtonStyle(color=ft.Colors.PRIMARY)
        )

        title_row = ft.Row(
            [
                self.title,
                ft.Row([self.unit_button, self.theme_button]),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.search_bar = ft.SearchBar(
            view_elevation=0,
            divider_color=ft.Colors.TRANSPARENT,
            bar_hint_text="Enter city name (e.g. London)",
            view_hint_text="Recent searches...",
            on_submit=self.on_search,
            on_tap=lambda e: self.search_bar.open_view(),
            
            # Default Light Mode Styles
            bar_bgcolor="#FFFFFF",
            bar_shape=ft.RoundedRectangleBorder(radius=10),
            bar_border_side=ft.BorderSide(1, "#718096"),
            bar_leading=ft.Icon(ft.Icons.LOCATION_CITY, color=ft.Colors.PRIMARY),
            bar_elevation=0,
            
            view_bgcolor="#FFFFFF",
            view_shape=ft.RoundedRectangleBorder(radius=10),
            view_size_constraints=ft.BoxConstraints(max_height=70),
            
            controls=[] 
        )
        
        self.location_button = ft.IconButton(
            icon=ft.Icons.MY_LOCATION,
            tooltip="Use Current Location",
            on_click=lambda e: self.page.run_task(self.get_current_location_weather),
            icon_color=ft.Colors.PRIMARY
        )
        
        self.search_button = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.ON_PRIMARY,
                bgcolor=ft.Colors.PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=10),
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
            bgcolor="#FFFFFF", # Default Light
            border_radius=20, 
            padding=25,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            )
        )
        
        self.error_message = ft.Text("", color=ft.Colors.RED_400, visible=False)
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
            self.show_error("Could not detect your location.")
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

    def get_weather_warnings(self, data: dict):
        """Analyze weather data and return a warning."""
        temp = data.get("main", {}).get("temp", 0)
        wind = data.get("wind", {}).get("speed", 0)
        weather_desc = data.get("weather", [{}])[0].get("main", "").lower()
        
        warning = None
        if temp > 35:
            warning = {
                "msg": f"🔥 Extreme Heat Alert! ({temp:.1f}°C)\nWear sunscreen.",
                "color": ft.Colors.RED_100,
                "icon": ft.Icons.LOCAL_FIRE_DEPARTMENT,
                "icon_color": ft.Colors.RED
            }
        elif temp > 30:
            warning = {
                "msg": f"☀️ High Temp Warning ({temp:.1f}°C)\nStay hydrated.",
                "color": ft.Colors.AMBER_100,
                "icon": ft.Icons.WARNING,
                "icon_color": ft.Colors.AMBER
            }
        elif temp < 5:
            warning = {
                "msg": f"❄️ Freeze Warning! ({temp:.1f}°C)",
                "color": ft.Colors.BLUE_100,
                "icon": ft.Icons.AC_UNIT,
                "icon_color": ft.Colors.BLUE
            }
        elif wind > 15:
            warning = {
                "msg": f"💨 High Wind Alert! ({wind} m/s)",
                "color": ft.Colors.GREY_300,
                "icon": ft.Icons.AIR,
                "icon_color": ft.Colors.GREY_700
            }
        elif "rain" in weather_desc:
            warning = {
                "msg": "🌧️ Rain Detected. Bring an umbrella!",
                "color": ft.Colors.BLUE_GREY_100,
                "icon": ft.Icons.UMBRELLA,
                "icon_color": ft.Colors.BLUE_GREY_700
            }
        return warning

    # --- LIFESTYLE METHOD ---
    async def get_lifestyle_content(self, weather_main, temp, city, timezone_offset):
        """Get lifestyle content (AI or Hardcoded fallback)."""
        
        utc_now = datetime.datetime.utcnow()
        local_time = utc_now + datetime.timedelta(seconds=timezone_offset)
        hour = local_time.hour
        
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        # 1. Try AI Generation
        try:
            ai_content = await self.ai_service.generate_lifestyle_content(weather_main, temp, city, time_of_day)
            
            # Icon mapping
            icon_map = {
                "clear": ft.Icons.WB_SUNNY,
                "cloud": ft.Icons.CLOUD_QUEUE,
                "rain": ft.Icons.WATER_DROP,
                "thunder": ft.Icons.FLASH_ON,
                "snow": ft.Icons.AC_UNIT
            }
            
            icon = ft.Icons.MUSIC_NOTE
            weather_key = weather_main.lower()
            for key, val in icon_map.items():
                if key in weather_key:
                    icon = val
                    break
            
            return {
                "fact": ai_content.get("fact", "Weather is interesting!"),
                "music": ai_content.get("music", "Weather with You - Crowded House"),
                "explanation": ai_content.get("music_explanation", "Fits the vibe."),
                "music_icon": icon,
                "fact_icon": ft.Icons.LIGHTBULB,
            }
            
        except Exception:
            return self.get_hardcoded_lifestyle(weather_main)

    def get_hardcoded_lifestyle(self, weather_main):
        """Fallback hardcoded content."""
        weather_main = weather_main.lower()
        content = {
            "fact": "The fastest wind ever recorded on Earth was 253 mph.",
            "music": "Weather with You - Crowded House",
            "explanation": "A classic weather song.",
            "music_icon": ft.Icons.MUSIC_NOTE,
            "fact_icon": ft.Icons.LIGHTBULB,
        }
        
        if "clear" in weather_main:
            content["fact"] = "The sun is 400 times larger than the moon."
            content["music"] = "Here Comes The Sun - The Beatles"
            content["explanation"] = "Perfect for a sunny day."
            content["music_icon"] = ft.Icons.WB_SUNNY
        elif "cloud" in weather_main:
            content["fact"] = "Clouds can weigh more than a million pounds!"
            content["music"] = "Sweater Weather - The Neighbourhood"
            content["explanation"] = "Cozy vibes for cloudy weather."
            content["music_icon"] = ft.Icons.CLOUD_QUEUE
        elif "rain" in weather_main:
            content["fact"] = "Raindrops look like hamburger buns when falling."
            content["music"] = "Umbrella - Rihanna"
            content["explanation"] = "Stay dry out there!"
            content["music_icon"] = ft.Icons.WATER_DROP
            
        return content

    async def display_weather(self, data: dict, forecast_data: dict = None, is_cached: bool = False, timestamp: datetime.datetime = None, is_offline: bool = False):
        """Display weather information with cache status."""
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        
        # Save data for re-coloring later
        self.last_weather_data = data
        
        # --- COLOR PALETTE SETUP ---
        is_dark = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Use specific hex codes for consistency
        text_primary = "#F7FAFC" if is_dark else "#1A202C"
        text_secondary = "#A0AEC0" if is_dark else "#718096"
        card_bg = "#2D3748" if is_dark else "#FFFFFF"
        
        # Footer Text
        footer_text = "Live Data"
        footer_color = text_secondary
        
        if is_offline:
            time_diff = datetime.datetime.now() - timestamp
            mins_ago = int(time_diff.total_seconds() / 60)
            footer_text = f"Offline - Data from {mins_ago} mins ago"
            footer_color = ft.Colors.ORANGE_400
        elif is_cached:
            time_diff = datetime.datetime.now() - timestamp
            mins_ago = int(time_diff.total_seconds() / 60)
            footer_text = f"Updated {mins_ago} mins ago"
            footer_color = ft.Colors.GREEN_400
        
        self.current_unit = "metric"
        self.current_temp = data.get("main", {}).get("temp", 0)
        self.current_feels_like = data.get("main", {}).get("feels_like", 0)
        self.forecast_data = forecast_data 
        
        self.unit_button.text = "°C"
        self.unit_button.update()
        
        humidity = data.get("main", {}).get("humidity", 0)
        weather_main = data.get("weather", [{}])[0].get("main", "")
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        wind_gust = data.get("wind", {}).get("gust", 0)
        
        timezone_offset = data.get("timezone", 0)
        sunrise = datetime.datetime.utcfromtimestamp(data.get("sys", {}).get("sunrise", 0) + timezone_offset).strftime("%I:%M %p")
        sunset = datetime.datetime.utcfromtimestamp(data.get("sys", {}).get("sunset", 0) + timezone_offset).strftime("%I:%M %p")
        date_display = datetime.datetime.utcfromtimestamp(data.get("dt", 0) + timezone_offset)
        
        self.additional_info_row = ft.Row(
            [
                self.create_info_card(ft.Icons.WATER_DROP, "Humidity", f'{humidity}%', card_bg, text_primary, text_secondary),
                self.create_info_card(ft.Icons.AIR, "Wind Speed", f'{wind_speed} m/s', card_bg, text_primary, text_secondary),
                self.create_info_card(ft.Icons.WIND_POWER, "Gustiness", f'{wind_gust} m/s', card_bg, text_primary, text_secondary),
                self.create_info_card(ft.Icons.GAS_METER, "Pressure", f'{pressure} hPa', card_bg, text_primary, text_secondary),
            ],
            scroll="adaptive", alignment=ft.MainAxisAlignment.SPACE_EVENLY
        )
        self.additional_info_cards = self.additional_info_row.controls
        
        self.solar_row = ft.Row(
            [
                self.create_info_card(ft.Icons.SUNNY, "Sunrise", f'{sunrise}', card_bg, text_primary, text_secondary),
                self.create_info_card(ft.Icons.SUNNY, "Sunset", f'{sunset}', card_bg, text_primary, text_secondary)
            ],
            alignment=ft.MainAxisAlignment.SPACE_EVENLY
        )
        self.solar_events = self.solar_row.controls

        self.forecast_cards = []
        self.forecast_row = ft.Row(
            self.forecast_cards, 
            scroll="adaptive", 
            alignment=ft.MainAxisAlignment.SPACE_EVENLY
        )
        self.update_forecast_display() 

        # Store main text controls for easier updating later
        self.location_text = ft.Text(f"{city_name}, {country}", size=30, weight=ft.FontWeight.BOLD, color=text_primary, text_align=ft.TextAlign.CENTER, no_wrap=False)
        self.solar_title = ft.Text("Sunrise and Sunset", size=24, weight=ft.FontWeight.BOLD, color=text_primary)
        self.forecast_title = ft.Text("5-Day Forecast", size=24, weight=ft.FontWeight.BOLD, color=text_primary)

        self.temperature = ft.Text(
            f"{self.current_temp:.1f}°C",
            size=48,
            weight=ft.FontWeight.BOLD,
            color=text_primary, # Initial color
        )
        
        self.feelslike = ft.Text(
            f"Feels like {self.current_feels_like:.1f}°C", 
            size=16, 
            color=text_secondary
        )
        
        self.description = ft.Text(description, size=16, italic=True, color=text_secondary)

        # --- GET LIFESTYLE CONTENT WITH TIMEZONE ---
        lifestyle = await self.get_lifestyle_content(weather_main, self.current_temp, city_name, timezone_offset)
        self.last_lifestyle_data = lifestyle # Save for theme toggling
        
        # Trivia Card
        self.trivia_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row([ft.Icon(lifestyle["fact_icon"], size=16, color=text_primary), ft.Text("Trivia", size=12, weight=ft.FontWeight.BOLD, color=text_primary)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text(lifestyle["fact"], size=12, italic=True, no_wrap=False, text_align=ft.TextAlign.CENTER, color=text_secondary),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            border_radius=10,
            padding=10,
            expand=True, 
        )

        # Music Card
        self.music_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row([ft.Icon(lifestyle["music_icon"], size=16, color=text_primary), ft.Text("Music", size=12, weight=ft.FontWeight.BOLD, color=text_primary)], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Text(lifestyle["music"], size=12, italic=True, no_wrap=False, text_align=ft.TextAlign.CENTER, color=text_secondary),
                    ft.Text(f"({lifestyle['explanation']})", size=10, color=text_secondary, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            border_radius=10,
            padding=10,
            expand=True, 
        )

        # REARRANGED LAYOUT
        self.weather_container.content = ft.Column(
            [
                # 1. Location
                ft.Row([self.location_text], alignment=ft.MainAxisAlignment.CENTER),
                
                # 2. Temp & Description
                ft.Row(
                    [
                        ft.Column([self.temperature, self.feelslike], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Image(src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png", width=120, height=120),
                                    margin=ft.Margin(0, -11, 0, 0)
                                ),
                                self.description,
                            ],
                            spacing=-20,
                            alignment=ft.MainAxisAlignment.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                
                # 3. Additional Info
                self.additional_info_row,

                # 4. Trivia Card
                ft.Row([self.trivia_card]), 
                
                # 5. Music Suggestion
                ft.Row([self.music_card]), 
                
                ft.Divider(),
                
                # 6. Sunrise/Sunset
                self.solar_title,
                self.solar_row,
                
                ft.Divider(),
                
                # 7. Forecast
                self.forecast_title,
                self.forecast_row,
                
                ft.Text(footer_text, size=12, italic=True, color=footer_color)
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

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
        
        # 1. CHECK CACHE FIRST
        now = datetime.datetime.now()
        cache_key = city.lower()
        
        if cache_key in self.weather_cache:
            cached = self.weather_cache[cache_key]
            if now - cached['timestamp'] < self.CACHE_DURATION:
                await self.display_weather(
                    cached['weather'], 
                    cached['forecast'], 
                    is_cached=True, 
                    timestamp=cached['timestamp'],
                    is_offline=False
                )
                self.loading.visible = False
                self.page.update()
                return

        # 2. FETCH FROM API
        try:
            weather_data, forecast_data = await asyncio.gather(
                self.weather_service.get_weather(city),
                self.weather_service.get_forecast(city)
            )
            
            # 3. SAVE TO CACHE
            self.weather_cache[cache_key] = {
                "weather": weather_data,
                "forecast": forecast_data,
                "timestamp": now
            }
            
            await self.display_weather(weather_data, forecast_data, is_cached=False)
            self.add_to_history(city)
            
        except Exception as e:
            # 4. OFFLINE FALLBACK
            if cache_key in self.weather_cache:
                cached = self.weather_cache[cache_key]
                self.show_error("Offline Mode: Showing cached data.")
                await asyncio.sleep(1.5) 
                await self.display_weather(
                    cached['weather'], 
                    cached['forecast'], 
                    is_cached=True, 
                    timestamp=cached['timestamp'],
                    is_offline=True
                )
            else:
                self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    # Accepts colors for dynamic theming
    def create_info_card(self, icon, label, value, bgcolor="#FFFFFF", text_primary="#1A202C", text_secondary="#718096"):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=text_secondary),
                    ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=text_primary),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=bgcolor,
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