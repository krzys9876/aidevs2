from textwrap import dedent

from aidevslib import utils
import pprint
import time

pp = pprint.PrettyPrinter(width=160)

exercise = 'whoami'

facts: [str] = []


def make_prompt() -> str:
    prompt = "You are given facts about a person in Polish language. Guess who it is.\n\n"
    prompt += "Facts:\n"
    for f in facts:
        prompt += f"- {f}\n"
    prompt += dedent("""
        Rules:
        - Tell only full name of the person.
        - Answer only if you are 100% sure about the answer. If you are not sure, answer: I don't know
        """)
    return prompt


def get_fact() -> str:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    fact = exercise_response.result["hint"]
    print(f"got fact: {fact}")
    return fact


def do_exercise() -> None:
    answered = False
    retries = 0
    max_retries = 10
    answer = ""
    while not answered and retries<max_retries:
        retries += 1
        print(f"trying {retries} of {max_retries}...")
        facts.append(get_fact())
        answer = utils.chatgpt_completion_text(make_prompt(),"Tell me who it is","gpt-3.5-turbo",0.1)
        print(f"got answer: {answer}")
        if "I don't know" not in answer.capitalize():
            answered = True

    if not answered:
        print("FATAL")
        exit(1)

    auth_token = utils.get_auth_token_or_exit(exercise)
    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
