from aidevslib import utils
import requests

exercise = 'liar'
question = "What is the best known building in Rome?"


def verify_answer(to_verify: str) -> str:
    system_prompt = f"""
        You will be provided with a sentence. You are to could it be an answer to the question: 
        {question} Answer only YES or NO
        """
    user_prompt = to_verify
    result = utils.chatgpt_completion(system_prompt, user_prompt)
    verification: str = result.result["choices"][0]["message"]["content"]
    return verification


def send_question(token: str) -> utils.ResponseResult:
    url = f"{utils.main_url}/{utils.task_url_postfix}/{token}"
    # NOTE: no header required
    data = {"question": question}
    response = requests.post(url, data=data, verify=False)
    return utils.ResponseResult(response)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)

    answered = send_question(auth_token)
    print(answered.result)
    verified = verify_answer(answered.result["answer"])
    print(verified)

    result_response = utils.send_solution(auth_token, verified)
    if result_response.is_invalid():
        exit(3)
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
