import requests
import json
import os
from requests import Response

main_url = 'https://zadania.aidevs.pl'
token_url_postfix = 'token'
task_url_postfix = 'task'
answer_url_postfix = 'answer'
exercise = 'moderation'
my_api_key = os.getenv("AIDEVS_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_url = 'https://api.openai.com/v1/moderations'


class ResponseResult:
    def __init__(self, response: Response):
        self.status_code: int = response.status_code
        self.result: dict = response.json() if self.is_valid_status() else {}
        print(f"Response {self.status_code}")
        print(response.text)

    def is_valid_status(self) -> bool:
        return self.status_code == 200

    def is_valid(self) -> bool:
        return self.is_valid_status() and self.result["code"] == 0

    def is_invalid(self) -> bool:
        return not self.is_valid


def send_post_json(url: str, data: dict, header: dict = None) -> ResponseResult:
    post_headers: dict = {"Content-Type": "application/json"}
    if header is not None:
        post_headers = post_headers | header
    print(f"sending: {data}")
    response = requests.post(url, data=json.dumps(data), headers=post_headers, verify=False)
    return ResponseResult(response)


def send_get(url: str) -> ResponseResult:
    headers = {"Content-Type": "application/json"}
    print(f"getting: {url}")
    response = requests.get(url, headers=headers, verify=False)
    return ResponseResult(response)


def get_auth_token() -> ResponseResult:
    data = {"apikey": my_api_key}
    url = f"{main_url}/{token_url_postfix}/{exercise}"
    return send_post_json(url, data)


def get_exercise_contents(token: str) -> ResponseResult:
    url = f"{main_url}/{task_url_postfix}/{token}"
    return send_get(url)


def send_solution(token: str, answer) -> ResponseResult:
    data = {"answer": answer}
    url = f"{main_url}/{answer_url_postfix}/{token}"
    return send_post_json(url, data)


def moderate_item(item: str) -> int:
    header = {"Authorization": f"Bearer {openai_api_key}"}
    data = {"input": item}
    result = send_post_json(openai_url, data, header)
    flagged: bool = result.result["results"][0]["flagged"]
    return 1 if flagged else 0


def do_exercise() -> None:
    auth_token_response = get_auth_token()
    if auth_token_response.is_invalid():
        exit(1)
    auth_token = auth_token_response.result['token']
    print(f"got token {auth_token}")

    exercise_response = get_exercise_contents(auth_token)
    if exercise_response.is_invalid():
        exit(2)

    input_items: [str] = exercise_response.result["input"]
    output: [int] = list(map(moderate_item, input_items))
    print(f"got array {output}")

    result_response = send_solution(auth_token, output)
    if result_response.is_invalid():
        exit(3)
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
