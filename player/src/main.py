import flet as ft
from views.home_view import HomeView
from views.player_view import PlayerView
import pygame

async def main(page: ft.Page):
    page.title = "Music Player"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Retro Styling
    page.bgcolor = ft.Colors.BLACK
    page.theme_mode = ft.ThemeMode.DARK
    page.fonts = {
        "PressStart2P": "https://github.com/google/fonts/raw/main/ofl/pressstart2p/PressStart2P-Regular.ttf"
    }
    font_family = "PressStart2P"
    
    # Custom Theme
    page.theme = ft.Theme(font_family=font_family)

    # Initialize Pygame Mixer
    try:
        pygame.mixer.init()
    except pygame.error as e:
        print(f"Warning: Could not initialize mixer: {e}")

    # --- Navigation & Routing ---

    def route_change(route):
        page.views.clear()
        
        # Root View: File Selection
        page.views.append(HomeView(page))

        if page.route == "/play":
            page.views.append(PlayerView(page))
        
        page.update()

    async def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    def window_event(e):
        if e.data == "close":
            pygame.mixer.quit()
            page.window_close()
    
    page.on_window_event = window_event

    # Initial route
    page.views.clear()
    route_change(page.route)


ft.run(main=main)
