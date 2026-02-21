from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Track:
    path: str
    title: str
    artist: str
    album: str
    track_number: int
    duration: float

class AppState:
    def __init__(self):
        self.is_playing: bool = False
        self.audio_length: float = 0
        self.current_pos: float = 0.0
        self.is_slider_dragging: bool = False
        self.playing_file: Optional[str] = None
        self.now_playing_name: str = "No File Selected"
        self.playlist: List[Track] = []
        self.current_track_index: int = -1
        self.is_repeat_enabled: bool = False

app_state = AppState()
