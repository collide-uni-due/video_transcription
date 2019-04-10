import speech_recognition as sr
import os
import sys
import nltk
import tempfile
import pathlib as pl
import time
import subprocess

from pydub import AudioSegment
from .chunkize_audio import AudioSilenceChunker


class AudioTranscriber:

    def __init__(self, *, language="en-US", service="google", chunker=None,
                 request_timeout=5):
        self.language = language
        self.service = service

        if chunker is None:
            chunker = AudioSilenceChunker()
        self.chunker = chunker
        self.request_timeout = request_timeout

    def transcribe_audio_file_to_tokens_time(self, wav_file_path):
        """
        Transcribes wav audio file in given dir and writes the text and tokenized timestamped
        words into the output dir
        :param input_dir: directory the file is in
        :type input_dir:
        :param output_dir: directory the results are written to
        :type output_dir:
        :param video_name: name of wav audio file without ending
        :type video_name:
        :param cutout:
        :type cutout:
        :return:
        :rtype:
        """
        file_path = pl.Path(wav_file_path)
        video_name = file_path.stem

        input_audio = AudioSegment.from_wav(file_path)

        sentence_audios = self.chunker.split_sentences(input_audio)

        # write individual sentences to disk so they can be read in for speech recognition.
        # this list contains filename, start and end time
        with tempfile.TemporaryDirectory() as t_f:

            sentence_file_list = []
            for i, (sentence, (start_time, end_time)) in enumerate(sentence_audios):
                output_file_name = os.path.join(t_f, video_name + "_Chunk_{:03d}.wav".format(i))
                print("Exporting {}".format(output_file_name))
                sentence_file_list.append((output_file_name, start_time, end_time))
                sentence.export(output_file_name, format="wav")

            print("Finished splitting sentences and writing to disk")
            # send each sentences individually to speech api to work around audio length limit
            sentence_texts = []
            tokenized_words_with_time = []
            for sentence_file, start_time, end_time in sentence_file_list:
                rec = sr.Recognizer()
                rec.operation_timeout = self.request_timeout
                with sr.AudioFile(sentence_file) as source:
                    audio = rec.record(source)
                try:
                    if self.service == "google":
                        transcribed_audio = rec.recognize_google(audio, language=self.language)
                    if self.service == "bing":
                        time.sleep(5)
                        transcribed_audio = rec.recognize_bing(audio,
                                                               self.kwargs["Bing_Key"],
                                                               language=self.language)
                    if self.service == "cmu":
                        transcribed_audio = rec.recognize_sphinx(audio, language=self.language)

                    print("Transcribing file {}: {}".format(sentence_file, transcribed_audio))
                    sentence_texts.append(transcribed_audio)
                    tokenized_words = nltk.word_tokenize(transcribed_audio)

                    # estimate timestamp of word by looking at the position in the sentence
                    # and multiplying timespan with the fraction of position/len
                    timespan = end_time - start_time
                    sentence_length = len(tokenized_words)
                    for i, token in enumerate(tokenized_words):
                        position = i / sentence_length
                        guessed_time = int(start_time + timespan * position)
                        # time is in format milliseconds
                        item = {
                            "word": token,
                            "time": guessed_time
                        }
                        tokenized_words_with_time.append(item)


                except sr.UnknownValueError:
                    print("Could not transcribe audiofile: {}".format(sentence_file), file=sys.stderr)
                except sr.RequestError as e:
                    print("Reqeuest Failed")
                    print(e)
                except Exception as e:
                    print(e)

            sentence_sep = ".\n"
            if self.service == "bing":
                tokenized_words_with_time = [item for item in tokenized_words_with_time if item["word"] != "."]
                sentence_sep = "\n"
            transcribed_text = sentence_sep.join(sentence_texts) + "."
            return transcribed_text, tokenized_words_with_time


mp4_to_wav_command = ["ffmpeg", "-i"]


def convert_mp4_to_wav(file_path_mp4):
    file_path_mp4 = file_path_mp4.absolute()
    file_name = file_path_mp4.name
    file_name_wav = file_name + ".wav"
    file_path_wav = file_path_mp4.parent / file_name_wav

    command = mp4_to_wav_command + [str(file_path_mp4), str(file_path_wav)]
    process = subprocess.run(command,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

    if process.returncode != 0:
        print(process.returncode)
        print(process.stdout)
        print(process.stderr)
        raise Exception("Conversion was unsuccessful")

    return file_path_wav
