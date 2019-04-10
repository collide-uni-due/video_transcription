import unittest
import pathlib as pl
from video_transcription.transcribe import AudioTranscriber, convert_mp4_to_wav

video_path = pl.Path("lttt.mp4").absolute()
wav_path = video_path.parent / "lttt.mp4.wav"

class AudioTranscriberTest(unittest.TestCase):


    def test_transcription(self):

        transcriber = AudioTranscriber()
        transcribed_text = transcriber.transcribe_audio_file_to_tokens_time(wav_path)
        print(transcribed_text)



    def test_convert_mp4_to_wav(self):
        convert_mp4_to_wav(video_path)