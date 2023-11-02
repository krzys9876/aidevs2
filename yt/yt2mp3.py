from typing import Optional
from pytube import YouTube, Stream
from aidevslib import utils
import argparse
import pprint
import json

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
    with open(txt_file, "wb") as txt_file:
        txt_file.write(txt.encode('utf-8'))
    return True


def do_summarize(prompt: str, txt_file: str, summary_file: str) -> str | None:
    summary = None
    if summary_file is not None:
        with open(txt_file, "rt") as txt:
            txt_contents: str = txt.read()
        summary = utils.chatgpt_completion_text(txt_contents, prompt)
        with open(summary_file, "wb") as sum_file:
            sum_file.write(summary.encode('utf-8'))
    return summary


def summarize(txt_file: str, summary_file: str) -> bool:
    if summary_file is not None:
        print(f"summarizing to {summary_file}")
        do_summarize("tldr", txt_file, summary_file)
    return True


def find_keywords(txt_file: str, kw_file: str) -> str | None:
    keywords_txt = None
    if kw_file is not None:
        print(f"extracting keywords to {kw_file}")
        keywords_txt = do_summarize(
            """
            Extract maximum of ten keywords from the text. Write them in a form of JSON array. 
            Write JSON only, do not write anything else.
            """, txt_file, kw_file)
    return keywords_txt


if __name__ == '__main__':
    print("START")

    parser = argparse.ArgumentParser(description="transcribe YT video to text and a summary")
    parser.add_argument("-u", "--url", help="YT video URL", required=True)
    parser.add_argument("-a", "--audio-file", help="path and filename of the output mp3 file", required=True)
    parser.add_argument("-m", "--metadata-file", help="path and filename of the metadata file", required=True)
    parser.add_argument("-t", "--txt-file", help="path and filename of the output text file", required=True)
    parser.add_argument("-s", "--sum-file", help="path and filename of the output summary text file", required=False)
    parser.add_argument("-k", "--keyword-file", help="path and filename of the output keywords text file", required=False)
    args = parser.parse_args()

    print("Parsed arguments:")
    pp.pprint(args)

    if not download_audio(args.url, args.audio_file):
        exit(1)
    if not transcribe(args.audio_file, args.txt_file):
        exit(2)
    if not summarize(args.txt_file, args.sum_file):
        exit(3)
    keywords = find_keywords(args.txt_file, args.keyword_file)
    if keywords is None:
        exit(4)
    metadata = {"url": args.url, "keywords": keywords}
    with open(args.metadata_file, "wb") as md_file:
        md_file.write(json.dumps(metadata).encode("utf-8"))

    print("END")
