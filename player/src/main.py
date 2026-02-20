import flet as ft
import pygame
import requests
import tempfile
import os
import tkinter as tk
from tkinter import filedialog

async def main(page: ft.Page):
    page.title = "Music Player"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

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
    
    now_playing_txt = ft.Text("Now Playing: Ambient C Motion", size=20, weight=ft.FontWeight.BOLD)

    play_btn = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW,
        icon_size=50,
    )

    async def play_pause(e):
        nonlocal is_playing
        if not is_playing:
            # Check if music is paused or stopped
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            
            play_btn.icon = ft.Icons.PAUSE
            is_playing = True
        else:
            pygame.mixer.music.pause()
            play_btn.icon = ft.Icons.PLAY_ARROW
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
                nonlocal is_playing
                
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    
                    now_playing_txt.value = f"Now Playing: {file_name}"
                    now_playing_txt.update()
                    
                    play_btn.icon = ft.Icons.PAUSE
                    play_btn.update()
                    is_playing = True
                except pygame.error as e:
                    print(f"Error loading music: {e}")
                    now_playing_txt.value = f"Error loading: {file_name}"
                    now_playing_txt.update()

        except Exception as ex:
             print(f"Error picking file: {ex}")

    pick_file_btn = ft.ElevatedButton(
        "Pick Audio File",
        icon=ft.Icons.AUDIO_FILE,
        on_click=pick_file_click
    )

    page.add(
        ft.Column(
            [
                now_playing_txt,
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

ft.app(target=main)
