import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer


class SpeechToText:
    def __init__(self, model_path, sample_rate=16000):
        self.sample_rate = sample_rate
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.audio_queue = queue.Queue()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_queue.put(bytes(indata))

    def listen(self):
        """Generator: yields recognized text"""
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback
        ):
            print("🎤 Listening...")
            while True:
                data = self.audio_queue.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        yield text

stt = SpeechToText("vosk-model-small-en-us-0.15")

for text in stt.listen():
    print("You said:", text)

    if "stop" in text:
        print("🛑 Stopping")
        break