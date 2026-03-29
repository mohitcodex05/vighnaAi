import whisper

model = whisper.load_model("base")

result = model.transcribe("real.wav")

print(result["text"])
