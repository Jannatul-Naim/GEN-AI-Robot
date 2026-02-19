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
        self.stream = None
        self.mic_on = False

    def _callback(self, indata, frames, time, status):
        if self.mic_on:
            self.audio_queue.put(bytes(indata))

    def mic_on_start(self):
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

    def mic_off(self):
        self.mic_on = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("🔇 Mic OFF")

    def listen(self):
        while self.mic_on:
            data = self.audio_queue.get()
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").strip()
                if text:
                    yield text


def main():
    stt = SpeechToText("vosk-model-small-en-us-0.15")
    stt.mic_on_start()

    for sentence in stt.listen():
        print("You said:", sentence)

        if "stop" in sentence:
            stt.mic_off()
            break



main()