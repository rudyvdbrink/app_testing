import flet as ft
from state import app_state
import pygame
import asyncio

class PlayerView(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/play",
            bgcolor=ft.Colors.BLACK,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.page_ref = page
        self.font_family = "PressStart2P"
        
        # --- Controls ---
        
        self.now_playing_txt = ft.Text(
            app_state.now_playing_name, 
            size=10, 
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_ACCENT_400,
            font_family=self.font_family
        )

        self.slider = ft.Slider(
            min=0, 
            max=app_state.audio_length if app_state.audio_length > 0 else 100, 
            value=app_state.current_pos, 
            width=400,
            active_color=ft.Colors.GREEN_400,
            thumb_color=ft.Colors.GREEN_ACCENT_700,
            inactive_color=ft.Colors.GREY_900 if app_state.audio_length > 0 else ft.Colors.GREY_800
        )

        self.slider.on_change = self.on_slider_change
        self.slider.on_change_start = self.on_slider_change_start
        self.slider.on_change_end = self.on_slider_change_end

        self.play_icon = ft.Icon(ft.Icons.PAUSE if app_state.is_playing else ft.Icons.PLAY_ARROW, size=50, color=ft.Colors.BLACK)

        self.play_btn = ft.Container(
            content=self.play_icon,
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
            on_click=self.play_pause, 
        )

        self.appbar = ft.AppBar(
            title=ft.Text("Now Playing", font_family=self.font_family),
            bgcolor=ft.Colors.BLACK,
            center_title=True
        )

        self.controls = [
            ft.Column(
                [
                    self.now_playing_txt,
                    ft.Container(height=20),
                    self.slider,
                    ft.Container(height=20),
                    self.play_btn
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        ]
        
        # Start background task updater
        self.page_ref.run_task(self.update_slider)

    # --- Event Handlers ---

    def on_slider_change(self, e):
         try:
             # Seek functionality
             pos = float(e.control.value)
             pygame.mixer.music.play(start=pos)
             app_state.current_pos = pos
             
             self.play_icon.icon = ft.Icons.PAUSE
             self.play_btn.update()
             app_state.is_playing = True
         except Exception as ex:
             print(f"Seek error: {ex}")

    def on_slider_change_start(self, e):
        app_state.is_slider_dragging = True

    def on_slider_change_end(self, e):
        app_state.is_slider_dragging = False
        self.on_slider_change(e) # Perform seek on release

    async def play_pause(self, e):
        if not app_state.is_playing:
            # Check if music is paused or stopped
            if not pygame.mixer.music.get_busy():
                if app_state.playing_file:
                    pygame.mixer.music.play()
            else:
                pygame.mixer.music.unpause()
            
            self.play_icon.icon = ft.Icons.PAUSE
            app_state.is_playing = True
        else:
            pygame.mixer.music.pause()
            self.play_icon.icon = ft.Icons.PLAY_ARROW
            app_state.is_playing = False
        self.play_btn.update()

    async def update_slider(self):
        while True:
            # We check if the control is still mounted (part of the page)
            if app_state.is_playing and not app_state.is_slider_dragging and self.slider.page:
                try:
                    if pygame.mixer.music.get_busy():
                        # get_pos returns ms since play().
                        pos_ms = pygame.mixer.music.get_pos()
                        current_time = app_state.current_pos + (pos_ms / 1000.0)
                        
                        if current_time <= self.slider.max:
                            self.slider.value = current_time
                            self.slider.update()
                except Exception as e:
                    pass
            await asyncio.sleep(0.1)
