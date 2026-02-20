
import pyttsx3

class TextToSpeech:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

    def speak(self, text):
        print("🔊 Robot:", text)
        self.engine.say(text)
        self.engine.runAndWait()

def test():
    tts = TextToSpeech()
    tts.speak("If you can hear this, the TTS system is working!")

