import flet as ft
from state import app_state, Track
import pygame
import tkinter as tk
from tkinter import filedialog
import os
from tinytag import TinyTag

class HomeView(ft.View):
    def __init__(self, page: ft.Page):
        self.page_ref = page # Store page reference
        self.font_family = "PressStart2P"
        
        self.pick_folder_btn = ft.Container(
            content=ft.Text("SELECT FOLDER", color=ft.Colors.BLACK, font_family=self.font_family, weight=ft.FontWeight.BOLD),
            bgcolor=ft.Colors.GREEN_400,
            padding=20,
            border_radius=0,
            on_click=self.pick_folder_click,
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
                    self.pick_folder_btn
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

    async def pick_folder_click(self, _):
        try:
            # Tkinter workaround for folder dialog
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            
            folder_path = filedialog.askdirectory(
                title="Select Music Folder"
            )
            
            root.destroy()
            
            if folder_path:
                app_state.playlist.clear()
                
                audio_files = []
                for root_dir, _, files in os.walk(folder_path):
                    for file in files:
                        if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                            full_path = os.path.join(root_dir, file)
                            try:
                                tag = TinyTag.get(full_path)
                                track_title = tag.title if tag.title else file
                                artist = tag.artist if tag.artist else "Unknown"
                                album = tag.album if tag.album else "Unknown"
                                # Handle track number, sometimes it's "1/10" or just "1" or None
                                track_num_str = tag.track
                                track_num = 0
                                if track_num_str:
                                    try:
                                        track_num = int(str(track_num_str).split('/')[0])
                                    except:
                                        pass
                                
                                audio_files.append({
                                    "path": full_path,
                                    "title": track_title,
                                    "artist": artist,
                                    "album": album,
                                    "track_number": track_num,
                                    "duration": tag.duration if tag.duration else 0
                                })
                            except Exception as e:
                                print(f"Error reading metadata for {file}: {e}")
                
                # Sort by track number
                audio_files.sort(key=lambda x: x["track_number"])
                
                if not audio_files:
                    print("No audio files found in folder.")
                    return

                # Create Track objects
                for f in audio_files:
                    app_state.playlist.append(Track(
                        path=f["path"],
                        title=f["title"],
                        artist=f["artist"],
                        album=f["album"],
                        track_number=f["track_number"],
                        duration=f["duration"]
                    ))

                # Start playing the first track
                first_track = app_state.playlist[0]
                app_state.current_track_index = 0
                
                try:
                    app_state.audio_length = first_track.duration
                    app_state.current_pos = 0.0
                    
                    pygame.mixer.music.load(first_track.path)
                    pygame.mixer.music.play()
                    
                    app_state.now_playing_name = f"{first_track.title} - {first_track.artist}"
                    app_state.is_playing = True
                    app_state.playing_file = first_track.path

                    # Navigate to player view
                    await self.page_ref.push_route("/play")

                except pygame.error as e:
                    print(f"Error loading music: {e}")
                    app_state.now_playing_name = f"Error loading: {first_track.title}"

        except Exception as ex:
             print(f"Error picking folder: {ex}")
