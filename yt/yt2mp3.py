from typing import Optional
from pytube import YouTube, Stream
from aidevslib import utils


def get_worst_audio(handler: YouTube, subtype: str = "mp4") -> Optional[Stream]:
    return (
        handler.streams.filter(only_audio=True, subtype=subtype)
        .order_by("abr")  # average bitrate
        .first()
    )


if __name__ == '__main__':
    print("START")

    url = "https://www.youtube.com/watch?v=GRcpEpVNhRc"
    audio_file_name = "sample.mp3"
    audio_file_loc = utils.make_path(__file__, audio_file_name)
    txt_file_name = "sample.txt"
    txt_file_loc = utils.make_path(__file__, txt_file_name)
    tldr_file_name = "sample_tldr.txt"
    tldr_file_loc = utils.make_path(__file__, tldr_file_name)

    yt_handler = YouTube(url)
    audio = get_worst_audio(yt_handler)
    if audio is None:
        print("Error!")
    else:
        print(f"downloading to {audio_file_loc}")
        audio.download(filename=audio_file_loc)
        print(f"transcribing to {txt_file_loc}")
        txt = utils.openai_transcribe(audio_file_loc)
        with open(txt_file_loc, "wt") as txt_file:
            txt_file.write(txt)
        print(f"preparing tldr to {tldr_file_loc}")
        tldr = utils.chatgpt_completion_text(txt, "tldr")
        with open(tldr_file_loc, "wt") as tldr_file:
            tldr_file.write(tldr)

    print("END")
