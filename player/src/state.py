from dataclasses import dataclass
from typing import Optional

class AppState:
    def __init__(self):
        self.is_playing: bool = False
        self.audio_length: float = 0
        self.current_pos: float = 0.0
        self.is_slider_dragging: bool = False
        self.playing_file: Optional[str] = None
        self.now_playing_name: str = "No File Selected"

app_state = AppState()
