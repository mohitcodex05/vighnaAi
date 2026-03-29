import sounddevice as sd

def capture_audio(callback):
    def audio_callback(indata, frames, time, status):
        callback(indata.copy())

    stream = sd.InputStream(callback=audio_callback)
    stream.start()
    return stream
