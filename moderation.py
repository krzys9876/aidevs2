import os
from aidevslib import utils

exercise = 'moderation'
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_url = 'https://api.openai.com/v1/moderations'


def moderate_item(item: str) -> int:
    header = {"Authorization": f"Bearer {openai_api_key}"}
    data = {"input": item}
    result = utils.send_post_json(openai_url, data, header)
    flagged: bool = result.result["results"][0]["flagged"]
    return 1 if flagged else 0


def do_exercise() -> None:
    auth_token_response = utils.get_auth_token(exercise)
    if auth_token_response.is_invalid():
        exit(1)
    auth_token = auth_token_response.result['token']
    print(f"got token {auth_token}")

    exercise_response = utils.get_exercise_contents(auth_token)
    if exercise_response.is_invalid():
        exit(2)

    input_items: [str] = exercise_response.result["input"]
    output: [int] = list(map(moderate_item, input_items))
    print(f"got array {output}")

    result_response = utils.send_solution(auth_token, output)
    if result_response.is_invalid():
        exit(3)
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
