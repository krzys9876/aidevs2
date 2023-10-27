from aidevslib import utils

exercise = 'helloapi'


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token,exercise)

    cookie = exercise_response.result['cookie']
    print(f"got cookie {cookie}")

    result_response = utils.send_solution(auth_token, cookie)
    if result_response.is_invalid():
        exit(3)
    print(f"got result {result_response.result['msg']} / {result_response.result['note']}")


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
