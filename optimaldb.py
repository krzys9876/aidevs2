from multiprocessing import Pool

from aidevslib import utils
import pprint
import json

pp = pprint.PrettyPrinter(width=160)

exercise = 'optimaldb'


def get_db_file(url: str) -> dict:
    txt = utils.get_file(url, "optimaldb_input.json")
    js = json.loads(txt)
    return js


def reduce_db(name: str, infos: [str]) -> str:
    all_infos = "\n".join(infos)
    prompt = f"Oto fakty na temat osoby o imieniu {name}:\n"
    return utils.chatgpt_completion_text(
        system_prompt=f"{prompt}\n{all_infos}\n",
        user_prompt="Opisz te same fakty w jak najkrótszym tekście. "
                    "Postaraj się nie stracić żadnej informacji z tekstu. Możesz używać krótkich równoważników zdań. ",
        max_tokens=1000)


def reduce_for_person(name: str, infos: [str]) -> str:
    print(f"IMIĘ: {name}")
    chunk_size = 30
    info_chunks = [infos[i:i + chunk_size] for i in range(0, len(infos), chunk_size)]
    reduced = list(map(lambda i: reduce_db(name, i), info_chunks))
    pp.pprint(reduced)
    return "\n".join(reduced)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)

    db = get_db_file(exercise_response.result["database"])
    # db = get_db_file("https://zadania.aidevs.pl/data/3friends.json")
    kv_tuples = [(k, db[k]) for k in db.keys()]
    with Pool() as pool:
        joined_info = pool.starmap(reduce_for_person, kv_tuples)

    pp.pprint(joined_info)
    answer = "\n".join(joined_info)
    print(len(answer))
    if len(answer) > 9 * 1024:
        print("FATAL too long")
        exit(1)

    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
