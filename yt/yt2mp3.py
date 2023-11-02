from typing import Optional
from pytube import YouTube, Stream
from aidevslib import utils
import argparse
import pprint

pp = pprint.PrettyPrinter(width=160)


def get_worst_audio(handler: YouTube, subtype: str = "mp4") -> Optional[Stream]:
    return (
        handler.streams.filter(only_audio=True, subtype=subtype)
        .order_by("abr")  # average bitrate
        .first()
    )


def download_audio(yt_url: str, file_loc: str) -> bool:
    yt_handler = YouTube(yt_url)
    audio_stream = get_worst_audio(yt_handler)
    if audio_stream is None:
        print("Error opening YT url")
        return False
    else:
        print(f"downloading to {file_loc}")
        audio_stream.download(filename=file_loc)
        return True


def transcribe(audio_file: str, txt_file: str) -> bool:
    print(f"transcribing to {txt_file}")
    txt = utils.openai_transcribe(audio_file)
    with open(txt_file, "wt") as txt_file:
        txt_file.write(txt)
    return True


def summarize(txt_file: str, summary_file: str) -> bool:
    if summary_file is not None:
        with open(txt_file, "rt") as txt:
            txt_contents: str = txt.read()
        print(f"summarizing to {summary_file}")
        summary = utils.chatgpt_completion_text(txt_contents, "tldr")
        with open(sum_file_loc, "wt") as sum_file:
            sum_file.write(summary)
    return True


if __name__ == '__main__':
    print("START")

    parser = argparse.ArgumentParser(description="transcribe YT video to text and a summary")
    parser.add_argument("-u", "--url", help="YT video URL", required=True)
    parser.add_argument("-a", "--audio-file", help="path and filename of the output mp3 file", required=True)
    parser.add_argument("-t", "--txt-file", help="path and filename of the output text file", required=True)
    parser.add_argument("-s", "--sum-file", help="path and filename of the output summary text file", required=False)
    args = parser.parse_args()

    print("Parsed arguments:")
    pp.pprint(args)

    txt_file_loc = args.txt_file
    sum_file_loc = args.sum_file

    if not download_audio(args.url, args.audio_file):
        exit(1)
    if not transcribe(args.audio_file, args.txt_file):
        exit(2)
    if not summarize(args.txt_file, args.sum_file):
        exit(3)

    print("END")
