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
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    input_items: [str] = exercise_response.result["input"]
    output: [int] = list(map(moderate_item, input_items))
    print(f"got array {output}")

    utils.send_solution_or_exit(auth_token, output)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
