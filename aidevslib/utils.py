from typing import Any

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
openai_url_transcription = 'https://api.openai.com/v1/audio/transcriptions'


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
        return not self.is_valid()


def send_get(url: str) -> ResponseResult:
    headers = {"Content-Type": "application/json"}
    print(f"getting: {url}")
    response = requests.get(url, headers=headers, verify=False)
    return ResponseResult(response)


def get_file(url: str, file: str) -> str:
    if not os.path.exists(file):
        response = requests.get(url, headers={"Content-Type": "text/html; charset=utf-8"}, verify=False)
        if response.status_code != 200:
            print("FATAL")
            print(response)
            exit(1)
        with open(file, "wt") as f:
            f.write(response.text)

    with open(file, "rt") as f:
        text = f.read()
    return text


def send_post_json(url: str, data: dict, header: dict = None, verify: bool = False) -> ResponseResult:
    post_headers: dict = {"Content-Type": "application/json"}
    if header is not None:
        post_headers = post_headers | header
    print("Sending:")
    pp.pprint(data)
    response = requests.post(url, data=json.dumps(data), headers=post_headers, verify=verify)
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
    (code, success) = try_send_solution_or_exit(token, answer)
    if not success:
        exit(3)


def try_send_solution_or_exit(token: str, answer) -> (int, bool):
    try:
        result_response = send_solution(token, answer)
    except requests.exceptions.RequestException as e:
        pp.pprint(e)
        return -1, False

    pp.pprint(result_response.result)
    if result_response.is_invalid():
        return result_response.status_code, False
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")
    return result_response.status_code, True


def get_exercise_info_or_exit(token: str, exercise_name: str) -> ResponseResult:
    exercise_response = get_exercise_contents(token)
    if exercise_response.is_invalid():
        exit(2)

    return exercise_response


# NOTE: param: functions is deprecated (2023-11-14), use tools instead
def chatgpt_completion(system_prompt: str, user_prompt: Any, functions: [dict] = None, tools: [dict] = None,
                       model: str = "gpt-4", temperature: float = 1.0, max_tokens=None) -> ResponseResult:
    header = {f"Authorization": f"Bearer {openai_api_key}"}
    data = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "temperature": temperature
    }
    if functions is not None:
        data.update({"functions": functions})
    if tools is not None:
        data.update({"tools": tools, "tool_choice": "auto"})
    if max_tokens is not None:
        data.update({"max_tokens": max_tokens})
    result = send_post_json(openai_url_completion, data, header, False)
    return result


def chatgpt_completion_text(system_prompt: str, user_prompt: str, model: str = "gpt-4",
                            temperature: float = 1.0, max_tokens=None) -> str:
    result = chatgpt_completion(system_prompt=system_prompt, user_prompt=user_prompt, functions=None,
                                model=model, temperature=temperature, max_tokens=max_tokens)
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

def openai_transcribe(file: str) -> str:
    # Uwaga: nagłówek bez: "Content-Type": "multipart/form-data"
    header = {"Authorization": f"Bearer {openai_api_key}"}
    with open(file, "rb") as file_to_send:
        # files: zawiera wyłącznie plki
        files = {"file": ("file1.mp3", open(file, "rb"), "application/octet-stream")}
        # Uwaga: pole data NIE jako JSON, ale tablica (k,v)
        data = [("model", "whisper-1")]
        response = requests.request(method="post", url=openai_url_transcription, files=files, data=data, headers=header)
        result = ResponseResult(response)
        transcribed = result.result["text"]
    return transcribed
