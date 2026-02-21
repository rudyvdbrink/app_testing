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
            width=300,
            active_color=ft.Colors.GREEN_400,
            thumb_color=ft.Colors.GREEN_ACCENT_700,
            inactive_color=ft.Colors.GREY_900 if app_state.audio_length > 0 else ft.Colors.GREY_800
        )

        self.slider.on_change = self.on_slider_change
        self.slider.on_change_start = self.on_slider_change_start
        self.slider.on_change_end = self.on_slider_change_end

        self.play_icon = ft.Icon(ft.Icons.PAUSE if app_state.is_playing else ft.Icons.PLAY_ARROW, size=30, color=ft.Colors.BLACK)

        self.play_btn = ft.Container(
            content=self.play_icon,
            width=60,
            height=60,
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

        # Prev/Next Buttons using retro styling
        self.prev_btn = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS,
            icon_color=ft.Colors.GREEN_400,
            icon_size=30,
            on_click=self.prev_track
        )

        self.next_btn = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT,
            icon_color=ft.Colors.GREEN_400,
            icon_size=30,
            on_click=self.next_track
        )

        self.repeat_btn = ft.IconButton(
            icon=ft.Icons.REPEAT,
            icon_color=ft.Colors.GREY_600,
            icon_size=20,
            on_click=self.toggle_repeat,
            tooltip="Enable Repeat"
        )

        self.appbar = ft.AppBar(
            title=ft.Text("Now Playing", font_family=self.font_family),
            bgcolor=ft.Colors.BLACK,
            center_title=True
        )

        # Playlist View
        self.track_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            auto_scroll=False
        )
        self.build_playlist_ui()

        self.controls = [
            ft.Column(
                [
                    self.track_list,
                    self.now_playing_txt,
                    ft.Container(height=10),
                    self.slider,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Container(self.repeat_btn, margin=ft.margin.only(right=20)), # Add some margin
                            self.prev_btn, 
                            self.play_btn, 
                            self.next_btn
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    ft.Container(height=20),
                ],
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True
            )
        ]
        
        # Start background task updater
        self.page_ref.run_task(self.update_slider)

    def build_playlist_ui(self):
        self.track_list.controls.clear()
        for idx, track in enumerate(app_state.playlist):
            is_current = idx == app_state.current_track_index
            self.track_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.MUSIC_NOTE, color=ft.Colors.GREEN_ACCENT_400 if is_current else ft.Colors.GREY_600, size=16),
                        ft.Text(
                            f"{track.track_number}. {track.title}", 
                            color=ft.Colors.GREEN_ACCENT_400 if is_current else ft.Colors.WHITE,
                            font_family=self.font_family,
                            size=10,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            expand=True
                        ),
                        ft.Text(
                            self.format_time(track.duration),
                            color=ft.Colors.GREY_500,
                            font_family=self.font_family,
                            size=10
                        )
                    ]),
                    padding=10,
                    bgcolor=ft.Colors.GREY_900 if is_current else ft.Colors.TRANSPARENT,
                    data=idx,
                    on_click=self.on_track_click
                )
            )

    async def on_track_click(self, e):
        idx = e.control.data
        if idx is not None:
            await self.play_track_by_index(idx)

    def format_time(self, seconds):
        if not seconds: return "0:00"
        m, s = divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    # --- Event Handlers ---

    async def toggle_repeat(self, e):
        app_state.is_repeat_enabled = not app_state.is_repeat_enabled
        self.repeat_btn.icon_color = ft.Colors.GREEN_400 if app_state.is_repeat_enabled else ft.Colors.GREY_600
        self.repeat_btn.update()

    async def play_track_by_index(self, index):
        if 0 <= index < len(app_state.playlist):
            app_state.current_track_index = index
            track = app_state.playlist[index]
            await self.load_and_play_track(track)
            self.build_playlist_ui()
            self.track_list.update()

    async def next_track(self, e):
        if app_state.current_track_index + 1 < len(app_state.playlist):
            await self.play_track_by_index(app_state.current_track_index + 1)

    async def prev_track(self, e):
        if app_state.current_track_index - 1 >= 0:
            await self.play_track_by_index(app_state.current_track_index - 1)

    async def load_and_play_track(self, track):
        try:
            pygame.mixer.music.load(track.path)
            pygame.mixer.music.play()
            
            app_state.current_pos = 0.0
            app_state.audio_length = track.duration
            app_state.is_playing = True
            app_state.playing_file = track.path
            app_state.now_playing_name = f"{track.title} - {track.artist}"

            # Update UI controls
            self.now_playing_txt.value = app_state.now_playing_name
            self.now_playing_txt.update()
            
            self.slider.max = track.duration if track.duration > 0 else 100
            self.slider.value = 0
            self.slider.inactive_color = ft.Colors.GREY_900 if track.duration > 0 else ft.Colors.GREY_800
            self.slider.update()

            self.play_icon.icon = ft.Icons.PAUSE
            self.play_btn.update()

        except Exception as e:
            print(f"Error playing track: {e}")
            self.now_playing_txt.value = f"Error: {track.title}"
            self.now_playing_txt.update()

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
                    # NEW: Check for Auto-Next Track when song ends
                    elif not pygame.mixer.music.get_busy() and app_state.is_playing:
                         # Music stopped busy but we think it should be playing -> ended
                         app_state.is_playing = False
                         self.play_icon.icon = ft.Icons.PLAY_ARROW
                         self.play_btn.update()
                         # Auto advance
                         if app_state.current_track_index + 1 < len(app_state.playlist):
                             await self.play_track_by_index(app_state.current_track_index + 1)
                         elif app_state.is_repeat_enabled and len(app_state.playlist) > 0: 
                             # Loop back to start if repeat is enabled
                             await self.play_track_by_index(0)

                except Exception as e:
                    pass
            await asyncio.sleep(0.1)
