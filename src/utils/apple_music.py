"""Apple Music integration via AppleScript"""

import subprocess
from typing import Dict, Optional

class AppleMusicPlayer:
    """Interface with Apple Music via AppleScript"""
    
    @staticmethod
    def run_script(script: str) -> str:
        """Run an AppleScript and return the result"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"AppleScript error: {e}")
            return ""
    
    @staticmethod
    def get_current_track() -> Optional[Dict]:
        """Get currently playing track info"""
        script = """
        tell application "Music"
            if player state is playing then
                set trackName to name of current track
                set artistName to artist of current track
                set albumName to album of current track
                return trackName & " | " & artistName & " | " & albumName
            else
                return "Not playing"
            end if
        end tell
        """
        result = AppleMusicPlayer.run_script(script)
        
        if result and result != "Not playing":
            parts = result.split(" | ")
            if len(parts) >= 3:
                return {
                    'track': parts[0],
                    'artist': parts[1],
                    'album': parts[2],
                    'is_playing': True
                }
        
        return {'is_playing': False, 'track': 'Not playing'}
    
    @staticmethod
    def play_pause():
        """Toggle play/pause"""
        script = """
        tell application "Music"
            playpause
        end tell
        """
        AppleMusicPlayer.run_script(script)
    
    @staticmethod
    def next_track():
        """Skip to next track"""
        script = """
        tell application "Music"
            next track
        end tell
        """
        AppleMusicPlayer.run_script(script)
    
    @staticmethod
    def previous_track():
        """Go to previous track"""
        script = """
        tell application "Music"
            previous track
        end tell
        """
        AppleMusicPlayer.run_script(script)
    
    @staticmethod
    def is_music_running() -> bool:
        """Check if Music app is running"""
        script = """
        tell application "System Events"
            if exists process "Music" then
                return "true"
            else
                return "false"
            end if
        end tell
        """
        result = AppleMusicPlayer.run_script(script)
        return result == "true"