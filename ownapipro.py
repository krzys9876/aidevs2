from aidevslib import utils
import pprint

pp = pprint.PrettyPrinter(width=160)

exercise = 'ownapipro'


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)

    answer = "https://_:_/apipro"
    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")


