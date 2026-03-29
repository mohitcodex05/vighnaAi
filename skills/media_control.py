"""
skills/media_control.py — Volume and media key control on Windows
Uses pycaw for volume and keyboard for media keys
"""

import subprocess


def _run(args):
    subprocess.run(args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def volume_up(step: int = 10) -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        import math

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = min(1.0, current + step / 100)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Volume set to {int(new_vol * 100)}%"
    except Exception:
        _run(["powershell", "-c",
              f"$wsh = New-Object -com wscript.shell; "
              f"for($i=0;$i<{step//2};$i++){{$wsh.SendKeys([char]175)}}"])
        return "Volume increased"


def volume_down(step: int = 10) -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current = volume.GetMasterVolumeLevelScalar()
        new_vol = max(0.0, current - step / 100)
        volume.SetMasterVolumeLevelScalar(new_vol, None)
        return f"Volume set to {int(new_vol * 100)}%"
    except Exception:
        _run(["powershell", "-c",
              f"$wsh = New-Object -com wscript.shell; "
              f"for($i=0;$i<{step//2};$i++){{$wsh.SendKeys([char]174)}}"])
        return "Volume decreased"


def mute_volume() -> str:
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        muted = volume.GetMute()
        volume.SetMute(not muted, None)
        return "Unmuted" if muted else "Muted"
    except Exception:
        _run(["powershell", "-c",
              "$wsh = New-Object -com wscript.shell; $wsh.SendKeys([char]173)"])
        return "Toggled mute"


def media_play_pause() -> str:
    _run(["powershell", "-c",
          "$wsh = New-Object -com wscript.shell; $wsh.SendKeys([char]179)"])
    return "Play/Pause toggled"


def media_next() -> str:
    _run(["powershell", "-c",
          "$wsh = New-Object -com wscript.shell; $wsh.SendKeys([char]176)"])
    return "Skipped to next track"


def media_previous() -> str:
    _run(["powershell", "-c",
          "$wsh = New-Object -com wscript.shell; $wsh.SendKeys([char]177)"])
    return "Went to previous track"


def handle_media_intent(clean_text: str) -> str | None:
    if "volume up" in clean_text or "increase volume" in clean_text or "louder" in clean_text:
        return volume_up()
    if "volume down" in clean_text or "decrease volume" in clean_text or "quieter" in clean_text:
        return volume_down()
    if "mute" in clean_text or "unmute" in clean_text:
        return mute_volume()
    if any(p in clean_text for p in ["pause music", "pause song", "play music", "resume music"]):
        return media_play_pause()
    if "next song" in clean_text or "next track" in clean_text or "skip song" in clean_text:
        return media_next()
    if "previous song" in clean_text or "prev track" in clean_text or "last song" in clean_text:
        return media_previous()
    return None

METADATA = {
    "name": "media",
    "description": "Control system volume and media playback keys.",
    "intents": ["volume", "mute", "unmute", "play", "pause", "next", "previous", "skip"]
}

def execute(action: str, args: dict) -> str:
    if action == "volume_up": return volume_up(args.get("step", 10))
    if action == "volume_down": return volume_down(args.get("step", 10))
    if action == "mute": return mute_volume()
    if action == "play_pause": return media_play_pause()
    if action == "next": return media_next()
    if action == "previous": return media_previous()
    # Fallback to text parsing if no specific action
    return handle_media_intent(args.get("query", "")) or "Unknown media action."
