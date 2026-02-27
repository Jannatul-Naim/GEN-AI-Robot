import json
import queue
import numpy as np
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import samplerate  # pip install samplerate


class SpeechToText:
    def __init__(self, model_path):
        self.device_index = 8              # ← your mic
        self.input_rate = 44100            # ← your mic rate
        self.target_rate = 16000           # ← Vosk best rate

        print("🎧 Using ALC897 Analog Mic (Index 8)")

        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.target_rate)

        self.q = queue.Queue(maxsize=50)
        self.stream = None
        self.mic_on = False

    def callback(self, indata, frames, time, status):
        if self.mic_on:
            try:
                self.q.put_nowait(bytes(indata))
            except queue.Full:
                pass

    def start(self):
        self.mic_on = True

        self.stream = sd.RawInputStream(
            device=self.device_index,
            samplerate=self.input_rate,
            blocksize=2048,
            dtype="int16",
            channels=1,
            latency="low",
            callback=self.callback,
        )

        self.stream.start()
        print("🎤 Mic ON")

    def stop(self):
        self.mic_on = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        print("🔇 Mic OFF")

    def resample(self, data):
        audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)

        ratio = self.target_rate / self.input_rate
        audio = samplerate.resample(audio, ratio, "sinc_fastest")

        audio = audio.astype(np.int16)
        return audio.tobytes()

    def listen(self):
        while self.mic_on:
            data = self.q.get()
            data = self.resample(data)

            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    yield text

def test_stt():
    model_path = "speech/models/vosk-model-small-en-us-0.15"
    stt = SpeechToText(model_path)

    stt.start()
    print("🎤 Speak something...")

    try:
        for text in stt.listen():
            print(f"🗣️ You said: {text}")
            if text.lower() in ("quit", "exit", "stop"):
                break
    except KeyboardInterrupt:
        pass
    finally:
        stt.stop()

# if __name__ == "__main__":
#     test_stt()