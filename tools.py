from aidevslib import utils
import pprint
import json
from datetime import datetime

pp = pprint.PrettyPrinter(width=160)

exercise = 'tools'

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_to_calendar",
            "description": "adds a task with a given date to the calendar",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "task description"},
                    "date": {"type": "string", "description": "task date"},
                },
                "required": ["task", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_todo_list",
            "description": "adds a task without a date to todo list",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "task description"},
                },
                "required": ["task"]
            }
        }
    }
]

prompt = ("Prepare a function call based on a given sentence. "
          "Choose a calendar task only when date is given. Choose todo task list otherwise.\n\n"
          "Try to derive date from the sentence using current date.\n"
          "Facts:\n"
          f"- Today is {datetime.today().strftime("%Y-%m-%d")}\n\n"
          "Rules:\n"
          "- Use the same language as used in the given sentence."
          "- Rephrase tasks to be verbless sentences"
          "- Use date format YYYY-MM-DD\n\n")


def decode_answer(function_name: str, args: dict) -> dict | None:
    match function_name:
        case "add_to_todo_list":
            answer = {"tool": "ToDo", "desc": args["task"]}
        case "add_to_calendar":
            answer = {"tool": "Calendar", "desc": args["task"], "date": args["date"]}
        case _:
            answer = None
    return answer


# finish_reason = "stop" - API responds with message/content/json object
def get_answer_from_stop(full_result: dict) -> str | None:
    function_call = json.loads(full_result["message"]["content"])
    # the API randomly returns $kind, $type, $invoke, $schema, sometimes w/o "$" etc.
    function_type_list = list(filter(lambda k: k[0] == "$", function_call.keys()))
    if len(function_type_list) > 0:
        function_type_key = function_type_list[0]
    else:
        function_type_key = list(function_call.keys())[0]

    function_type = function_call[function_type_key]
    if function_type is None or "functions." not in function_type:
        print("FATAL not a function call")
        exit(1)
    pp.pprint(function_call)
    function_name = function_type.replace("functions.", "")
    return decode_answer(function_name, function_call)


# finish_reason = "tool_calls" - API responds with message/tool_calls/[json object]
def get_answer_from_tool_calls(full_result: dict) -> str | None:
    # get first call only
    function_call = full_result["message"]["tool_calls"][0]
    function_type = function_call["type"]
    if "function" not in function_type:
        print("FATAL not a function call")
        exit(1)
    pp.pprint(function_call)
    function_name = function_call["function"]["name"]
    function_args = json.loads(function_call["function"]["arguments"])
    return decode_answer(function_name, function_args)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)
    question = exercise_response.result["question"]

    # NOTE: new unstable API (2023-11-14)
    response = utils.chatgpt_completion(system_prompt=prompt, user_prompt=question, tools=tools, model="gpt-4")
    answer = None
    full_result = response.result["choices"][0]
    match full_result["finish_reason"]:
        case "stop":
            answer = get_answer_from_stop(full_result)
        case "tool_calls":
            answer = get_answer_from_tool_calls(full_result)

    if answer is None:
        print("FATAL no answer")
        exit(2)

    print(f"got answer: {answer}")
    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
