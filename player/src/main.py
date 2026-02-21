import flet as ft
import pygame
import requests
import tempfile
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

    # Download and load audio file
    url = "https://luan.xyz/files/audio/ambient_c_motion.mp3"
    temp_dir = tempfile.gettempdir()
    local_file = os.path.join(temp_dir, "ambient_c_motion.mp3")
    
    # Simple check to avoid re-downloading every run if it exists
    if not os.path.exists(local_file):
        print(f"Downloading {url}...")
        try:
            response = requests.get(url)
            with open(local_file, "wb") as f:
                f.write(response.content)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading file: {e}")
            return

    try:
        pygame.mixer.music.load(local_file)
    except pygame.error as e:
        print(f"Error loading music: {e}")

    is_playing = False
    
    now_playing_txt = ft.Text(
        "Now Playing: Ambient C Motion", 
        size=10, 
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.GREEN_ACCENT_400,
        font_family=font_family
    )

    # Playback control variables
    audio_length = 0
    current_pos = 0.0 # Time where we last sought/started
    is_slider_dragging = False # Track if user is interacting
    playing_file = local_file # Default
    
    # Get duration of initial file
    try:
        sound = pygame.mixer.Sound(local_file)
        audio_length = sound.get_length()
    except:
         pass

    slider = ft.Slider(
        min=0, 
        max=audio_length, 
        value=0, 
        width=400,
        active_color=ft.Colors.GREEN_400,
        thumb_color=ft.Colors.GREEN_ACCENT_700,
        inactive_color=ft.Colors.GREY_900 if audio_length > 0 else ft.Colors.GREY_800
    )

    def on_slider_change(e):
         try:
             # Seek functionality
             nonlocal current_pos, is_playing
             pos = float(e.control.value)
             pygame.mixer.music.play(start=pos)
             current_pos = pos
             
             play_icon.icon = ft.Icons.PAUSE
             play_btn.update()
             is_playing = True
         except Exception as ex:
             print(f"Seek error: {ex}")

    def on_slider_change_start(e):
        nonlocal is_slider_dragging
        is_slider_dragging = True

    def on_slider_change_end(e):
        nonlocal is_slider_dragging
        is_slider_dragging = False
        on_slider_change(e) # Perform seek on release

    slider.on_change_start = on_slider_change_start
    slider.on_change_end = on_slider_change_end

    async def update_slider():
        while True:
            if is_playing and not is_slider_dragging:
                try:
                    if pygame.mixer.music.get_busy():
                        # get_pos returns ms since play().
                        # get_pos DOES generate time during unpause, it pauses counting during pause.
                        # So simply:
                        pos_ms = pygame.mixer.music.get_pos()
                        current_time = current_pos + (pos_ms / 1000.0)
                        
                        if current_time <= slider.max:
                            slider.value = current_time
                            slider.update()
                except Exception as e:
                    pass
            await asyncio.sleep(0.1)

    page.run_task(update_slider)

    # Retro Play Button
    play_icon = ft.Icon(ft.Icons.PLAY_ARROW, size=50, color=ft.Colors.BLACK)

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
        on_click=None, # Set below
    )

    async def play_pause(e):
        nonlocal is_playing
        if not is_playing:
            # Check if music is paused or stopped
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            
            play_icon.icon = ft.Icons.PAUSE
            is_playing = True
        else:
            pygame.mixer.music.pause()
            play_icon.icon = ft.Icons.PLAY_ARROW
            is_playing = False
        play_btn.update()

    play_btn.on_click = play_pause

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
                nonlocal is_playing, current_pos
                
                try:
                    s = pygame.mixer.Sound(file_path)
                    nonlocal audio_length
                    audio_length = s.get_length()
                    slider.max = audio_length
                    slider.value = 0
                    current_pos = 0.0
                    slider.update()

                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    
                    now_playing_txt.value = f"Now Playing: {file_name}"
                    now_playing_txt.update()
                    
                    play_icon.icon = ft.Icons.PAUSE
                    play_btn.update()
                    is_playing = True
                    
                    nonlocal playing_file
                    playing_file = file_path
                except pygame.error as e:
                    print(f"Error loading music: {e}")
                    now_playing_txt.value = f"Error loading: {file_name}"
                    now_playing_txt.update()

        except Exception as ex:
             print(f"Error picking file: {ex}")

    pick_file_btn = ft.Container(
        content=ft.Text("EJECT / LOAD", color=ft.Colors.BLACK, font_family=font_family, weight=ft.FontWeight.BOLD),
        bgcolor=ft.Colors.GREEN_400,
        padding=10,
        border_radius=0,
        on_click=pick_file_click,
        border=ft.Border(
            top=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            bottom=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            left=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
            right=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400)
        )
    )

    page.add(
        ft.Column(
            [
                now_playing_txt,
                slider,
                play_btn,
                pick_file_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )
    
    def window_event(e):
        if e.data == "close":
            pygame.mixer.quit()
            page.window_close()
    
    page.on_window_event = window_event


ft.run(main=main)
