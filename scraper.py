import time
from typing import Any

from aidevslib import utils
import pprint
import requests

pp = pprint.PrettyPrinter(width=160)

exercise = 'scraper'


def try_get_file(url: str) -> (int, str):
    headers = {"User-Agent": "Chrome/118.0.5993.118"}
    print(f"getting: {url}")
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=60)
        print(response.status_code)
        pp.pprint(response.text)
        return response.status_code, response.text
    except TimeoutError as e:
        pp.pprint(e)
        return -1, "TimeoutError"
    # base error in results
    except requests.exceptions.ConnectionError as e:
        pp.pprint(e)
        return -3, "ConnectionError"
    # base error in results
    except requests.exceptions.RequestException as e:
        pp.pprint(e)
        return -2, "RequestException"


def retry_loop(func, sleep_between: int, *args) -> (bool, Any):
    retries = 0
    max_retries = 10
    code = 0
    result = None
    while retries < max_retries and code != 200:
        retries += 1
        print(f"trying {retries} of {max_retries}...")
        (code, result) = func(*args)
        print(f"code: {code}")
        time.sleep(sleep_between)

    return code == 200, result


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    # polecenie dla chat GPT (Return answer for the question in POLISH language,
    # based on provided article. Maximum length for the answer is 200 characters)
    main_msg = exercise_response.result["msg"]
    pp.pprint(exercise_response.result)

    success, text = retry_loop(try_get_file, 1, exercise_response.result["input"])

    if not success:
        print("FATAL")
        exit(1)

    pp.pprint(text)

    answer = utils.chatgpt_completion_text(f"{main_msg}\n###\n{text}", exercise_response.result["question"])
    pp.pprint(answer)

    success, answer_result = retry_loop(utils.try_send_solution_or_exit, 1, auth_token, answer)
    if not success:
        print("FATAL")
        exit(2)

    pp.pprint(answer_result)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
