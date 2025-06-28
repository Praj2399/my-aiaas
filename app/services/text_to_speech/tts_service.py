import os 
from TTS.api import TTS
from tempfile import NamedTemporaryFile

models_dir = "ds_models"
os.environ["TTS_HOME"] = models_dir

class TTSService:
    def __init__(self, model_name="tts_models/en/ljspeech/tacotron2-DDC"):
        self.tts = TTS(model_name=model_name, progress_bar=True, gpu=False)

    def synthesize(self, text: str) -> str:
        with NamedTemporaryFile(delete=False, suffix=".wav") as f:
            self.tts.tts_to_file(text=text, file_path=f.name)
            return f.name
