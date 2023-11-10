import os.path

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import sqlite3
import requests
import json
import pprint
import embedding
import uuid

pp = pprint.PrettyPrinter(width=160)

BASE_PATH = "c:\\data\\docker\\"
SQLDB_PATH = f"{BASE_PATH}sqlite\\aidevs_search.sqlite"
QDRANT_PATH = f"{BASE_PATH}qdrant_local\\"
JSON_PATH = f"{BASE_PATH}\\tmp\\aidevs_search.json"
COLLECTION_NAME = "aidevs_search"
client = QdrantClient(path=QDRANT_PATH)
sqldb = sqlite3.connect(SQLDB_PATH)


def get_source() -> str:
    if not os.path.exists(JSON_PATH):
        response = requests.get("https://unknow.news/archiwum.json",
                                headers={"Content-Type": "text/html; charset=utf-8"}, verify=False)
        if response.status_code != 200:
            print("FATAL")
            print(response)
            exit(1)
        with open(JSON_PATH, "wt") as f:
            f.write(response.text)

    with open(JSON_PATH, "rt") as f:
        text = f.read()
    return text

def create_tables_if_not_exist() -> None:
    res = sqldb.execute(f"select count(*) from sqlite_master where type='table' and name='infos'")
    if res.fetchone()[0] == 1:
        print("table infos already exists")
    else:
        print("creating table infos")
        sqldb.execute("create table infos "
                      "(id int8, uuid text, title text, url text, info text, info_date date, emb_flag int2)")


def remove_parentheses(text: str) -> str:
    return text.replace('\"', '""')


def insert_info_if_not_exists(rec_id: int, rec_uuid: str, title: str, url: str, info: str, info_date: str) -> None:
    res = sqldb.execute(f"select count(*) from infos where id={rec_id}")
    if res.fetchone()[0] == 1:
        print(f"info {rec_id} already exists")
    else:
        print(f"inserting info {rec_id}")
        ninfo = remove_parentheses(info)
        ntitle = remove_parentheses(title)
        sqldb.execute(f"insert into infos (id, uuid, title, url, info, info_date, emb_flag) " 
                      f"values ({rec_id}, \"{rec_uuid}\", \"{ntitle}\", \"{url}\", \"{ninfo}\", \"{info_date}\",0)")


def get_all_non_processed_infos() -> []:
    cur = sqldb.cursor()
    cur.execute("select * from infos where emb_flag=0 order by id")
    return cur.fetchall()


def update_info_processed(rec_id: int) -> None:
    sqldb.execute(f"update infos set emb_flag=1 where id={rec_id} and emb_flag=0")
    sqldb.commit()


def create_collection_if_not_exists() -> None:
    colls = client.get_collections()
    if not colls.collections:
        print(f"creating collection {COLLECTION_NAME}")
        client.create_collection(collection_name=COLLECTION_NAME,
                                 vectors_config=VectorParams(size=1536, distance=Distance.COSINE, on_disk=True))
    else:
        print(f"found collection {COLLECTION_NAME}")


def copy_source_to_db(source) -> None:
    for idx, info in enumerate(source):
        insert_info_if_not_exists(idx, str(uuid.uuid4()), info["title"], info["url"], info["info"], info["date"])
    sqldb.commit()


def process_one_info(info: []) -> bool:
    # id, uuid, title, url, info, info_date, emb_flag
    try:
        emb_vector = embedding.calc_embedding(info[4])
        print(f"got embedding of length {len(emb_vector)}")
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=info[1], vector=emb_vector, payload={"id": str(info[0]), "url": info[3]})]
        )
        update_info_processed(info[0])
        # weryfikacja w qdrant
        check = client.search(collection_name=COLLECTION_NAME, query_vector=emb_vector, limit=1)
        if check:
            print(check[0].id)
            print(check[0].score)
            print(check[0].payload["id"])
            print(check[0].payload["url"])
        else:
            print("FATAL not found")
            exit(1)
        return True
    except requests.RequestException as e:
        print(e)
        print("ignoring...")
        return False


def do_exercise() -> None:
    create_tables_if_not_exist()
    create_collection_if_not_exists()
    # 300 wpisów powinno wystarczyć do rozwiązania zadania
    copy_source_to_db(json.loads(get_source())[:300])

    counter = 0
    for i in get_all_non_processed_infos():
        print(f"processing id {i[0]}")
        pp.pprint(i)
        if process_one_info(i):
            counter += 1

    print(f"processed: {counter}")
    sqldb.close()


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
