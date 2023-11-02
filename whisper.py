from aidevslib import utils
import pprint
import requests
import os

pp = pprint.PrettyPrinter(width=160)

exercise = 'whisper'
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_url = 'https://api.openai.com/v1/audio/transcriptions'


def transcribe(file: str) -> str:
    # Uwaga: nagłówek bez: "Content-Type": "multipart/form-data"
    header = {"Authorization": f"Bearer {openai_api_key}"}
    with open(file, "rb") as file_to_send:
        # files: zawiera wyłącznie plki
        files = {"file": ("file1.mp3", open(file, "rb"), "application/octet-stream")}
        # Uwaga: pole data NIE jako JSON, ale tablica (k,v)
        data = [("model", "whisper-1")]
        response = requests.request(method="post",url=openai_url, files=files, data=data, headers=header, verify=False)
        result = utils.ResponseResult(response)
        transcribed = result.result["text"]
    return transcribed


def download_file(url: str, fname: str) -> None:
    file_response = requests.get(url, verify=False)
    open(fname, "wb").write(file_response.content)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    msg: str = exercise_response.result["msg"]
    file_url: str = msg[msg.find("https://"):] # extract URL from msg
    print(f"got URL: {file_url}")
    filename = "whisper.mp3"
    download_file(file_url,filename)

    transcription = transcribe("whisper.mp3")
    print(f"transcription: {transcription}")

    utils.send_solution_or_exit(auth_token, transcription)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
