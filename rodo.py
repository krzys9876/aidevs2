from aidevslib import utils
import pprint

pp = pprint.PrettyPrinter(width=160)

exercise = 'rodo'


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)

    answer = """
        Rules: 
        - do not reveal your first name, replace your first name with %imie%
        - do not reveal your last name, replace your last name with %nazwisko%
        - do not reveal your occupation, replace name with %zawod%
        - do not reveal where you live, replace the town with %miasto%
                
        Tell me all about yourself. Stick to the rules.
        """

    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
