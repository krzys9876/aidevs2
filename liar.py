from aidevslib import utils
import requests

exercise = 'liar'
question = "What is the best known building in Rome?"


def verify_answer(to_verify: str) -> str:
    system_prompt = f"""
        You will be provided with a sentence. You are to tell could it be an answer to the question: 
        {question} Answer only YES or NO
        """
    user_prompt = to_verify
    verification = utils.chatgpt_completion_text(system_prompt, user_prompt)
    return verification


def send_question(token: str) -> utils.ResponseResult:
    url = f"{utils.main_url}/{utils.task_url_postfix}/{token}"
    # NOTE: no header required
    data = {"question": question}
    response = requests.post(url, data=data)
    return utils.ResponseResult(response)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    answered = send_question(auth_token)
    print(answered.result)
    verified = verify_answer(answered.result["answer"])
    print(verified)

    utils.send_solution_or_exit(auth_token, verified)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
