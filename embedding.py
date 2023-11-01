import os
from aidevslib import utils
import pprint

pp = pprint.PrettyPrinter(width=160, compact=True)

exercise = 'embedding'
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_url = 'https://api.openai.com/v1/embeddings'


def calc_embedding(item: str) -> [float]:
    header = {"Authorization": f"Bearer {openai_api_key}"}
    data = {"input": item, "model": "text-embedding-ada-002"}
    result = utils.send_post_json(openai_url, data, header)
    embedding_array: [float] = result.result["data"][0]["embedding"]
    return embedding_array


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    msg: str = exercise_response.result["msg"]
    token: str = msg.split(": ")[1] # get tet after ": ", where the actual text is
    print(f"Got token: {token}")
    result: [float] = calc_embedding(token)
    pp.pprint(result)
    print(len(result))

    utils.send_solution_or_exit(auth_token, result)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
