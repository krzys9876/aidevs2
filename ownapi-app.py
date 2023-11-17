from flask import Flask, request, Request
from aidevslib import utils
from pprint import PrettyPrinter

pp = PrettyPrinter(width=160)

app = Flask(__name__)


memory: [(str, str)] = []

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def ensure_post_json(request:Request) -> (bool, dict | None, int | None):
    if request.method != 'POST':
        return False, {'error': 'Sorry, I was waiting for POST'}, 400
    if not request.is_json:
        return False, {'error': 'Sorry, I was waiting for JSON'}, 400
    return True, None, None


@app.route('/api', methods=['POST', 'GET'])
def api_call():
    match ensure_post_json(request):
        case False, r, c: return r, c
        case _: pass

    formatted = pp.pformat(request.json)
    app.logger.info(f"Got this:\n{formatted}")
    question = request.json["question"]
    app.logger.info(f"Got question:\n{question}")
    try:
        reply = utils.chatgpt_completion_text("Odpowiedz krótko na pytanie.", question)
    except Exception as e:
        app.logger.info(f"Got exception:\n{str(e)}")
        return {'error': 'Sorry, got some error here...'}, 400
    app.logger.info(f"Got reply:\n{reply}")

    return {'reply': reply}, 200


@app.route('/apipro', methods=['POST', 'GET'])
def apipro_call():
    match ensure_post_json(request):
        case False, r, c: return r, c
        case _: pass

    formatted = pp.pformat(request.json)
    app.logger.info(f"Got this:\n{formatted}")
    question: str = request.json["question"]
    app.logger.info(f"Got question:\n{question}")
    # prepare prompt
    prompt = "Continue conversation. Answer briefly and concisely. Use single word in answer if possible.\n###\n"
    for (role, text) in memory:
        prompt = f"{prompt}\n{role}: {text}"
    # get reply
    try:
        reply = utils.chatgpt_completion_text(prompt, question)
    except Exception as e:
        app.logger.info(f"Got exception:\n{str(e)}")
        return {'error': 'Sorry, got some error here...'}, 400
    # format reply
    if reply.startswith("A:"):
        reply = reply[2:]
    app.logger.info(f"Got reply:\n{reply}")
    # memorize Q and A
    memory.append(("Q", question))
    memory.append(("A", reply))
    app.logger.info(pp.pformat(memory))

    return {'reply': reply}, 200


if __name__ == '__main__':
    app.run()
