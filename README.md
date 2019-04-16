This Library is designed to transcribe videos,
but can also be  used for audio files.

Steps:

Import the library
```python
from video_transcription import transcribe
```
Convert video file to wav.
For mp4 files there is a convenience function

```python
transcribe.convert_mp4_to_wav(path_to_mp4)
```
The wav file will be written in the same folder
with the same name as the mp4.
Once you have the wav file you can give it
as input to the transcriber

```python
ts = transcribe.AudioTranscriber()
text, word_time_tokens = ts.transcribe_audio_file_to_tokens_time(wav_path)
```
You will get back a tuple with two values.
The first is simply the text of the recording.
The second is a list of maps. Each map represents a word
and has the key "word" for the actual word and "time" for
the time in seconds for where it appeared in the recording (There is some
interpolation used so it might not be completely accurate)
The transcriber takes an optional language parameter
, but defaults to english. By default it uses
a free cloud transcription service from google.
Further choices can be implemented if there is demand.
Since the library depends on the 
[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
library, all available transcription methods can
be added.
