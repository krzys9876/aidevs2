from aidevslib import utils

exercise = 'helloapi'


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token,exercise)

    cookie = exercise_response.result['cookie']
    print(f"got cookie {cookie}")

    utils.send_solution_or_exit(auth_token, cookie)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
