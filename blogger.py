from aidevslib import utils

exercise = 'blogger'


def write_blog_post(topic: str) -> str:
    system_prompt = "Jesteś bloggerem kulinarnym, znasz się na robieniu pizzy Margherity."
    user_prompt = f"Napisz krótki wpis (trzy zdania) na blogu na temat: {topic}".encode("utf-8", "strict").decode()
    result = utils.chatgpt_completion(system_prompt, user_prompt)
    blog_post: str = result.result["choices"][0]["message"]["content"]
    return blog_post


def do_exercise() -> None:
    auth_token_response = utils.get_auth_token(exercise)
    if auth_token_response.is_invalid():
        exit(1)
    auth_token = auth_token_response.result['token']
    print(f"got token {auth_token}")

    exercise_response = utils.get_exercise_contents(auth_token)
    if exercise_response.is_invalid():
        exit(2)

    input_items: [str] = exercise_response.result["blog"]
    output: [str] = list(map(write_blog_post, input_items))
    print(f"got array {output}")

    result_response = utils.send_solution(auth_token, output)
    if result_response.is_invalid():
        exit(3)
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
