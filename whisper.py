from aidevslib import utils
import pprint
import requests

pp = pprint.PrettyPrinter(width=160)

exercise = 'whisper'


def download_file(url: str, fname: str) -> None:
    file_response = requests.get(url, verify=False)
    open(fname, "wb").write(file_response.content)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    # extract URL from msg
    msg: str = exercise_response.result["msg"]
    file_url: str = msg[msg.find("https://"):]
    print(f"got URL: {file_url}")
    file_loc = utils.make_path(__file__, "whisper.mp3")
    print(f"target file: {file_loc}")
    download_file(file_url, file_loc)

    transcription = utils.openai_transcribe(file_loc)
    pp.pprint(f"transcription: {transcription}")

    utils.send_solution_or_exit(auth_token, transcription)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
