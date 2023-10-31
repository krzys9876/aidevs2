from aidevslib import utils
import pprint

pp = pprint.PrettyPrinter(width=120)

exercise = 'inprompt'


def extract_name(sentence: str) -> str:
    system_prompt = f"""
        You will be provided with a sentence in Polish. This sentence contains a name. Find the name. 
        Write the name only. 
        """
    user_prompt = sentence
    result = utils.chatgpt_completion(system_prompt, user_prompt)
    name: str = result.result["choices"][0]["message"]["content"]
    return name


def answer_question(context: [str], question: str) -> str:
    context_txt = "\n".join(context)
    system_prompt = f"Masz za zadanie odpowiedzieć na pytanie. Oto informacje, które mogą być pomocne:\n{context_txt}"
    user_prompt = question
    answer = utils.chatgpt_completion_text(system_prompt, user_prompt)
    return answer


def is_important(sentence: str, name: str) -> bool:
    return sentence.find(name) >= 0


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    infos = exercise_response.result["input"]
    question = exercise_response.result["question"]
    print(question)
    name = extract_name(question)
    print(name)
    # pp.pprint(infos)
    infos_important = list(filter(lambda s: is_important(s, name), infos))
    pp.pprint(infos_important)
    answer = answer_question(infos_important, question)
    print(answer)

    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
