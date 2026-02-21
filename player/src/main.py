import flet as ft
import pygame
import os
import tkinter as tk
from tkinter import filedialog
import asyncio

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

    # State variables
    state = {
        "is_playing": False,
        "audio_length": 0,
        "current_pos": 0.0, # Time where we last sought/started
        "is_slider_dragging": False, # Track if user is interacting
        "playing_file": None,
        "now_playing_name": "No File Selected"
    }

    # --- Controls ---
    
    now_playing_txt = ft.Text(
        state["now_playing_name"], 
        size=10, 
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_ACCENT_400,
        font_family=font_family
    )

    slider = ft.Slider(
        min=0, 
        max=100, 
        value=0, 
        width=400,
        active_color=ft.Colors.GREEN_400,
        thumb_color=ft.Colors.GREEN_ACCENT_700,
        inactive_color=ft.Colors.GREY_900
    )

    play_icon = ft.Icon(ft.Icons.PLAY_ARROW, size=50, color=ft.Colors.BLACK)
    
    # We need to define play_btn before we can update it in functions, 
    # but we need functions defined before we can assign them to play_btn.on_click.
    # So we create container first and assign on_click later or access it via variables.

    # --- Event Handlers ---

    def on_slider_change(e):
         try:
             # Seek functionality
             pos = float(e.control.value)
             pygame.mixer.music.play(start=pos)
             state["current_pos"] = pos
             
             play_icon.icon = ft.Icons.PAUSE
             play_btn.update()
             state["is_playing"] = True
         except Exception as ex:
             print(f"Seek error: {ex}")

    def on_slider_change_start(e):
        state["is_slider_dragging"] = True

    def on_slider_change_end(e):
        state["is_slider_dragging"] = False
        on_slider_change(e) # Perform seek on release

    slider.on_change = on_slider_change
    slider.on_change_start = on_slider_change_start
    slider.on_change_end = on_slider_change_end

    async def play_pause(e):
        if not state["is_playing"]:
            # Check if music is paused or stopped
            if not pygame.mixer.music.get_busy():
                if state["playing_file"]:
                    pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            
            play_icon.icon = ft.Icons.PAUSE
            state["is_playing"] = True
        else:
            pygame.mixer.music.pause()
            play_icon.icon = ft.Icons.PLAY_ARROW
            state["is_playing"] = False
        play_btn.update()

    play_btn = ft.Container(
        content=play_icon,
        width=80,
        height=80,
        bgcolor=ft.Colors.GREEN_400,
        border_radius=0, # Square
        border=ft.Border(
            top=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            bottom=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            left=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            right=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400)
        ),
        alignment=ft.Alignment(0, 0),
        on_click=play_pause, 
    )

    async def pick_file_click(_):
        try:
            # Tkinter workaround for file dialog
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            
            file_path = filedialog.askopenfilename(
                title="Select Audio File", 
                filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
            )
            
            root.destroy()
            
            if file_path:
                file_name = os.path.basename(file_path)
                
                try:
                    s = pygame.mixer.Sound(file_path)
                    state["audio_length"] = s.get_length()
                    
                    # Update info
                    slider.max = state["audio_length"]
                    slider.value = 0
                    state["current_pos"] = 0.0
                    
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    
                    state["now_playing_name"] = f"Now Playing: {file_name}"
                    now_playing_txt.value = state["now_playing_name"]
                    
                    play_icon.icon = ft.Icons.PAUSE
                    state["is_playing"] = True
                    state["playing_file"] = file_path

                    # Navigate to player view
                    await page.push_route("/play")

                except pygame.error as e:
                    print(f"Error loading music: {e}")
                    state["now_playing_name"] = f"Error loading: {file_name}"

        except Exception as ex:
             print(f"Error picking file: {ex}")

    pick_file_btn = ft.Container(
        content=ft.Text("SELECT FILE", color=ft.Colors.BLACK, font_family=font_family, weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.GREEN_400,
        padding=20,
        border_radius=0,
        on_click=pick_file_click,
        border=ft.Border(
            top=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            bottom=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            left=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            right=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400)
        )
    )

    # --- Background Tasks ---

    async def update_slider():
        while True:
            if state["is_playing"] and not state["is_slider_dragging"]:
                try:
                    if pygame.mixer.music.get_busy():
                        # get_pos returns ms since play().
                        pos_ms = pygame.mixer.music.get_pos()
                        current_time = state["current_pos"] + (pos_ms / 1000.0)
                        
                        if current_time <= slider.max:
                            slider.value = current_time
                            # Only update if the slider is currently added to the page
                            if slider.page:
                                slider.update()
                except Exception as e:
                    pass
            await asyncio.sleep(0.1)

    page.run_task(update_slider)

    # --- Navigation & Routing ---

    def route_change(route):
        page.views.clear()
        
        # Root View: File Selection
        page.views.append(
            ft.View(
                route="/",
                controls=[
                    ft.AppBar(
                        title=ft.Text("Music Player", font_family=font_family),
                        bgcolor=ft.Colors.BLACK,
                        center_title=True
                    ),
                    ft.Column(
                        [
                            ft.Text("INSERT DISK", font_family=font_family, color=ft.Colors.GREEN_ACCENT_400),
                            ft.Container(height=20),
                            pick_file_btn
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    )
                ],
                bgcolor=ft.Colors.BLACK,
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        if page.route == "/play":
            page.views.append(
                ft.View(
                    route="/play",
                    controls=[
                        ft.AppBar(
                            title=ft.Text("Now Playing", font_family=font_family),
                            bgcolor=ft.Colors.BLACK,
                            center_title=True
                        ),
                        ft.Column(
                            [
                                now_playing_txt,
                                ft.Container(height=20),
                                slider,
                                ft.Container(height=20),
                                play_btn
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=True
                        )
                    ],
                    bgcolor=ft.Colors.BLACK,
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        
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
