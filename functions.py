from aidevslib import utils
import pprint
import json

pp = pprint.PrettyPrinter(width=160)

exercise = 'functions'


def define_function() -> dict:
    return {
        "name": "addUser",
        "description": "some example function",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "user name"
                },
                "surname": {
                    "type": "string",
                    "description": "user surname"
                },
                "year": {
                    "type": "integer",
                    "description": "year of birth"
                }
            },
            "required": ["name", "surname", "year"]
        }
    }

def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    schema = define_function()
    pp.pprint(schema)

    utils.send_solution_or_exit(auth_token, schema)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")

