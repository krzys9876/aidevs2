from aidevslib import utils
import pprint
import json
import sqlite3

pp = pprint.PrettyPrinter(width=160)

exercise = 'people'

JSON_PATH = "people.json"
SQLDB_PATH = "people.sqlite"
sqldb = sqlite3.connect(SQLDB_PATH)


def create_tables_if_not_exist() -> None:
    res = sqldb.execute(f"select count(*) from sqlite_master where type='table' and name='people_info'")
    if res.fetchone()[0] == 1:
        print("table already exists")
    else:
        print("creating table")
        sqldb.execute("create table people_info "
                      "(id int8, fname text, lname text, info text, color text)")


def insert_info_if_not_exists(rec_id: int, fname: str, lname: str, info: str, color: str) -> None:
    res = sqldb.execute(f"select count(*) from people_info where id={rec_id}")
    if res.fetchone()[0] == 1:
        print(f"{rec_id} already exists")
    else:
        print(f"inserting {rec_id}")
        sqldb.execute(f"insert into people_info (id, fname, lname, info, color) "
                      f"values ({rec_id}, \"{fname}\", \"{lname}\", \"{info}\", \"{color}\")")


def find_info(fname: str, lname: str) -> []:
    cur = sqldb.cursor()
    cur.execute(f"select * from people_info where fname='{fname}' and lname='{lname}'")
    return cur.fetchone()


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)

    create_tables_if_not_exist()
    source = utils.get_file(exercise_response.result["data"], JSON_PATH)
    for i, info in enumerate(json.loads(source)):
        print(f"inserting: {i}|{info["imie"]}|{info["nazwisko"]}|{info["o_mnie"][:10]}...|{info["ulubiony_kolor"]}")
        insert_info_if_not_exists(i, info["imie"], info["nazwisko"], info["o_mnie"], info["ulubiony_kolor"])
    sqldb.commit()

    question = exercise_response.result["question"]
    full_name = utils.chatgpt_completion_text(
        'Jesteś asystentem kierującym pytania do odpowiednich osób. W podanym zdaniu znajdź imię i nazwisko '
        'i wypisz je w formacie json {"first_name" : imię, "last_name" : nazwisko}. '
        'Przykład: '
        'Jak nazywa się pies Jana Kowalskiego - {"first_name" : "Jan", "last_name" : "Kowalski"}',
        question,"gpt-3.5-turbo")

    full_name_json = json.loads(full_name)
    pp.pprint(full_name_json)
    if "first_name" not in full_name_json or "last_name" not in full_name_json:
        print("FATAL: incorrect json")
        exit(1)
    person_info = find_info(full_name_json["first_name"],full_name_json["last_name"])
    pp.pprint(person_info)

    answer = utils.chatgpt_completion_text(
        "Odpowiedz na pytanie używając podanych informacji:"
        f"Nazywam się {person_info[1]} {person_info[2]},"
        f"{person_info[3]}."
        f"Mój ulubiony kolor to {person_info[4]}",
        question,"gpt-3.5-turbo")

    print(f"got answer: {answer}")

    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    sqldb.close()
    print("END")
