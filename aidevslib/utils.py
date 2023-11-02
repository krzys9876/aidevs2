import requests
from requests import Response
import json
import os
import pprint

pp = pprint.PrettyPrinter(width=160)

main_url = 'https://zadania.aidevs.pl'
token_url_postfix = 'token'
task_url_postfix = 'task'
answer_url_postfix = 'answer'
my_api_key = os.getenv('AIDEVS_API_KEY')
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_url_completion = 'https://api.openai.com/v1/chat/completions'


class ResponseResult:
    def __init__(self, response: Response):
        self.status_code: int = response.status_code
        self.result: dict = response.json() if self.is_valid_status() else {}
        print(f"Response {self.status_code}:")
        pp.pprint(response.text)

    def is_valid_status(self) -> bool:
        return self.status_code == 200

    def is_valid(self) -> bool:
        return self.is_valid_status() and self.result["code"] == 0

    def is_invalid(self) -> bool:
        return not self.is_valid


def send_get(url: str) -> ResponseResult:
    headers = {"Content-Type": "application/json"}
    print(f"getting: {url}")
    response = requests.get(url, headers=headers, verify=False)
    return ResponseResult(response)


def send_post_json(url: str, data: dict, header: dict = None) -> ResponseResult:
    post_headers: dict = {"Content-Type": "application/json"}
    if header is not None:
        post_headers = post_headers | header
    print("Sending:")
    pp.pprint(data)
    response = requests.post(url, data=json.dumps(data), headers=post_headers, verify=False)
    return ResponseResult(response)


def get_auth_token_or_exit(exercise: str) -> str:
    data = {"apikey": my_api_key}
    url = f"{main_url}/{token_url_postfix}/{exercise}"
    auth_token_response = send_post_json(url, data)
    if auth_token_response.is_invalid():
        exit(1)
    return auth_token_response.result['token']


def get_exercise_contents(token: str) -> ResponseResult:
    url = f"{main_url}/{task_url_postfix}/{token}"
    return send_get(url)


def send_solution(token: str, answer) -> ResponseResult:
    data = {"answer": answer}
    url = f"{main_url}/{answer_url_postfix}/{token}"
    return send_post_json(url, data)


def send_solution_or_exit(token: str, answer) -> None:
    result_response = send_solution(token, answer)
    if result_response.is_invalid():
        exit(3)
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")



def get_exercise_info_or_exit(token: str, exercise_name: str) -> ResponseResult:
    exercise_response = get_exercise_contents(token)
    if exercise_response.is_invalid():
        exit(2)

    return exercise_response


def chatgpt_completion(system_prompt: str, user_prompt: str, model: str = "gpt-4",
                       temperature: float = 1.0) -> ResponseResult:
    header = {f"Authorization": f"Bearer {openai_api_key}"}
    data = {
        "model": "gpt-4",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": 1
    }
    result = send_post_json(openai_url_completion, data, header)
    return result


def chatgpt_completion_text(system_prompt: str, user_prompt: str, model: str = "gpt-4",
                            temperature: float = 1.0) -> str:
    result = chatgpt_completion(system_prompt, user_prompt, model, temperature)
    return result.result["choices"][0]["message"]["content"]


def make_path(base, file_name: str) -> str:
    curr_dir = os.path.dirname(base)
    separator = os.path.sep
    return f"{curr_dir}{separator}{file_name}"


#  curl https://api.openai.com/v1/audio/transcriptions
#  -H "Authorization: Bearer $OPENAI_API_KEY"
#  -H "Content-Type: multipart/form-data"
#  -F file="@whisper.mp3"
#  -F model="whisper-1"

def openai_transcribe(api_url: str, file: str) -> str:
    # Uwaga: nagłówek bez: "Content-Type": "multipart/form-data"
    header = {"Authorization": f"Bearer {openai_api_key}"}
    with open(file, "rb") as file_to_send:
        # files: zawiera wyłącznie plki
        files = {"file": ("file1.mp3", open(file, "rb"), "application/octet-stream")}
        # Uwaga: pole data NIE jako JSON, ale tablica (k,v)
        data = [("model", "whisper-1")]
        response = requests.request(method="post", url=api_url, files=files, data=data, headers=header)
        result = ResponseResult(response)
        transcribed = result.result["text"]
    return transcribed
