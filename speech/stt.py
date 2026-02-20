
import json
import queue


import sounddevice as sd
from vosk import Model, KaldiRecognizer


import os
import sys



class SpeechToText:
    def __init__(self, model_path, sample_rate=16000):
        self.sample_rate = sample_rate
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.audio_queue = queue.Queue()
        self.stream = None
        self.mic_on = False

    def _callback(self, indata, frames, time_info, status):
        if self.mic_on:
            self.audio_queue.put(bytes(indata))

    def start(self):
        if self.mic_on:
            return
        self.mic_on = True
        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=self._callback
        )
        self.stream.start()
        print("🎤 Mic ON")

    def stop(self):
        self.mic_on = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("🔇 Mic OFF")

    def listen(self):
        """
        Yields full sentences only (AcceptWaveform = complete utterance)
        """
        while self.mic_on:
            data = self.audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    yield text



def test():
    # ---- Safe Absolute Path ----
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-small-en-us-0.15")

    if not os.path.exists(MODEL_PATH):
        print("❌ Model path not found:", MODEL_PATH)
        sys.exit(1)

    stt = SpeechToText(MODEL_PATH)

    try:
        stt.start()
        print("🎙 Say something... (say 'stop' to exit)\n")

        for text in stt.listen():
            print("You said:", text)

            if text.lower() in ("stop", "exit", "quit"):
                print("🛑 Stopping...")
                break

    except KeyboardInterrupt:
        print("\n⌨ Interrupted by user.")

    finally:
        stt.stop()


