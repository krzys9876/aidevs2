from aidevslib import utils

exercise = 'blogger'


def write_blog_post(topic: str) -> str:
    system_prompt = "Jesteś bloggerem kulinarnym, znasz się na robieniu pizzy Margherity."
    user_prompt = f"Napisz krótki wpis (trzy zdania) na blogu na temat: {topic}".encode("utf-8", "strict").decode()
    blog_post = utils.chatgpt_completion_text(system_prompt, user_prompt)
    return blog_post


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    input_items: [str] = exercise_response.result["blog"]
    output: [str] = list(map(write_blog_post, input_items))
    print(f"got array {output}")

    utils.send_solution_or_exit(auth_token, output)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
