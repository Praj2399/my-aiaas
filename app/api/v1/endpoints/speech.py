from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
from services.speech_to_text.whisper_service import WhisperService
from services.text_to_speech.tts_service import TTSService

router = APIRouter()
whisper_service = WhisperService()
tts_service = TTSService()

@router.post("/speech-to-text/")
async def speech_to_text(file: UploadFile = File(...)):
    contents = await file.read()
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)
    result = whisper_service.transcribe(temp_path)
    return {"text": result}

@router.post("/text-to-speech/")
async def text_to_speech(text: str):
    audio_path = tts_service.synthesize(text)
    return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")
