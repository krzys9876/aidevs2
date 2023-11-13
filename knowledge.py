from aidevslib import utils
import pprint
import json

pp = pprint.PrettyPrinter(width=160)

exercise = 'knowledge'

functions = [
    {
        "name": "get_population",
        "description": "gets population of the given country",
        "parameters": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "country name"},
            },
            "required": ["country"]
        },
    },
    {
        "name": "get_exchange_rate",
        "description": "gets current exchange rate of the given currency to fixed default currency",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {"type": "string", "description": "currency for which exchange rate is required"},
            },
            "required": ["currency"]
        },
    },
    {
        "name": "general_question",
        "description":
            "a function returning answer to general question not related to exchange rates and countries' populations",
        "parameters": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "a general question"},
            },
            "required": ["question"]
        },
    }
]

prompt = ("You will be asked questions about a population of a given country, exchange rate of a given currency "
          "and other general question. For country name use English name only. "
          "For currency use currency symbol according to ISO 4217. For general questions use the same language.")


def get_population(country: str) -> int:
    # Knowledge about countries https://restcountries.com/ - field 'population'
    facts = utils.send_get(f"https://restcountries.com/v3.1/name/{country}?fields=name,population")
    pp.pprint(facts.result)
    return facts.result[0]["population"]


def get_exchange_rate(currency: str) -> float:
    # Currency http://api.nbp.pl/en.html (use table A)"
    rates = utils.send_get(f"https://api.nbp.pl/api/exchangerates/rates/A/{currency}/last/")
    pp.pprint(rates.result)
    return rates.result["rates"][0]["mid"]


def general_question(question: str) -> str:
    return utils.chatgpt_completion_text("Odpowiedz krótko i zwięźle na pytanie",question)

def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)
    question = exercise_response.result["question"]

    #question = "podaj aktualny kurs EURO"
    #question = "jaki jest teraz kurs dolara"
    #question = "kto napisał Romeo i Julię?"
    #question = "podaj populację Francji"

    response = utils.chatgpt_completion(system_prompt=prompt, user_prompt=question, functions=functions)
    pp.pprint(response)
    full_result = response.result["choices"][0]
    if full_result["finish_reason"] != "function_call":
        print("FATAL not a function call")
        exit(1)
    function_call = full_result["message"]["function_call"]
    function_name = function_call["name"]
    function_arguments = json.loads(function_call["arguments"])
    answer = None
    match function_name:
        case "get_population": answer = get_population(function_arguments["country"])
        case "get_exchange_rate": answer = get_exchange_rate(function_arguments["currency"])
        case "general_question": answer = general_question(function_arguments["question"])

    # answer = get_population("France")
    # answer = get_exchange_rate("EUR")

    print(f"got answer: {answer}")
    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
