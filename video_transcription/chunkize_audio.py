from pydub import silence


class AudioSilenceChunker:

    def __init__(self, *, min_silence_len=1, silence_threshold=10):
        self.silence_threshold = silence_threshold
        # need silence in milliseconds for pydub
        self.min_silence_len = min_silence_len * 1000

    def split_sentences(self, input_audio):
        # read in file and split on periods of silence
        average_volume = input_audio.dBFS
        silence_thresh = average_volume - self.silence_threshold
        # silence_thresh = average_volume
        print("Average Volume of the file is: {}".format(average_volume))
        sentence_audios = split_on_silence(input_audio,
                                           min_silence_len=self.min_silence_len,
                                           silence_thresh=silence_thresh)

        return sentence_audios


def split_on_silence(audio_segment,
                     min_silence_len=1000,
                     silence_thresh=-16,
                     keep_silence=100,
                     split_range_threshold=30000):
    """
    audio_segment - original pydub.AudioSegment() object

    min_silence_len - (in ms) minimum length of a silence to be used for
        a split. default: 1000ms

    silence_thresh - (in dBFS) anything quieter than this will be
        considered silence. default: -16dBFS

    keep_silence - (in ms) amount of silence to leave at the beginning
        and end of the chunks. Keeps the sound from sounding like it is
        abruptly cut off. (default: 100ms)
    """

    not_silence_ranges = silence.detect_nonsilent(audio_segment, min_silence_len, silence_thresh)

    not_silence_ranges = split_large_ranges(not_silence_ranges, split_range_threshold)
    not_silence_ranges = split_large_ranges(not_silence_ranges, split_range_threshold)

    chunks = []

    for start_i, end_i in not_silence_ranges:
        start_i = max(0, start_i - keep_silence)
        end_i += keep_silence
        chunks.append((audio_segment[start_i:end_i], (start_i, end_i)))

    return chunks


def split_large_ranges(ranges, size_threshold):
    result_ranges = []
    for start_i, end_i in ranges:

        time_diff = end_i - start_i
        if time_diff > size_threshold:
            print("split block of size {}".format(time_diff))
            mid_point = start_i + time_diff / 2
            chunk_1 = (start_i, mid_point)
            chunk_2 = (mid_point, end_i)
            result_ranges.append(chunk_1)
            result_ranges.append(chunk_2)
        else:
            result_ranges.append((start_i, end_i))
    return result_ranges
