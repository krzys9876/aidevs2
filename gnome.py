from aidevslib import utils
import pprint
import json

pp = pprint.PrettyPrinter(width=160)

exercise = 'gnome'


# sample image:
# https://zadania.aidevs.pl/gnome/ed8e9ba8625ad433a86d8250f6908d36.png
def describe_image(url:str) -> str:
    user_prompt = [
        {"type": "text", "text": "Jeżeli na obrazku jest skrzat i ma on czapkę, podaj kolor czapki. Jeżeli na obrazku nie ma skrzata, odpowiedz słowem ERROR."},
        {"type": "image_url", "image_url": url}
    ]
    result = utils.chatgpt_completion(
        system_prompt="Odpowiedz na pytanie dotyczące obrazka. Odpowiedz tylko jednym słowem, zgodnie z instrukcją.",
        user_prompt=user_prompt, model="gpt-4-vision-preview")
    pp.pprint(result.result)
    return result.result["choices"][0]["message"]["content"]


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)

    url = exercise_response.result["url"]
    print(f"got url: {url}")
    answer = describe_image(url)
    print(f"got answer: {answer}")

    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")

