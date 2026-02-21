import flet as ft
from state import app_state
import pygame
import tkinter as tk
from tkinter import filedialog
import os

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        self.page_ref = page # Store page reference
        self.font_family = "PressStart2P"
        
        self.pick_file_btn = ft.Container(
            content=ft.Text("SELECT FILE", color=ft.Colors.BLACK, font_family=self.font_family, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.GREEN_400,
            padding=20,
            border_radius=0,
            on_click=self.pick_file_click,
            border=ft.Border(
                top=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
                bottom=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
                left=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400),
                right=ft.BorderSide(2, ft.Colors.GREEN_ACCENT_400)
            )
        )

        controls = [
            ft.AppBar(
                title=ft.Text("Music Player", font_family=self.font_family),
                bgcolor=ft.Colors.BLACK,
                center_title=True
            ),
            ft.Column(
                [
                    ft.Text("INSERT DISK", font_family=self.font_family, color=ft.Colors.GREEN_ACCENT_400),
                    ft.Container(height=20),
                    self.pick_file_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        ]
        
        super().__init__(
            route="/",
            controls=controls,
            bgcolor=ft.Colors.BLACK,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

    async def pick_file_click(self, _):
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
                    app_state.audio_length = s.get_length()
                    app_state.current_pos = 0.0
                    
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                    
                    app_state.now_playing_name = f"Now Playing: {file_name}"
                    app_state.is_playing = True
                    app_state.playing_file = file_path

                    # Navigate to player view
                    await self.page_ref.push_route("/play")

                except pygame.error as e:
                    print(f"Error loading music: {e}")
                    app_state.now_playing_name = f"Error loading: {file_name}"

        except Exception as ex:
             print(f"Error picking file: {ex}")
