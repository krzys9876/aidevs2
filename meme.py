import os
from aidevslib import utils
import pprint

pp = pprint.PrettyPrinter(width=160)

exercise = 'meme'
renderio_api_key = os.getenv("RENDERIO_API_KEY")


# curl --request POST \
#      --url https://get.renderform.io/api/v2/render \
#      --header 'X-API-KEY: <API_KEY>' \
#      --header 'Content-Type: application/json' \
#      --data '{
#             "template": "<TEMPLATE_ID>",
#             "data": {
#               "my-text-component-id.color": "#eeeeee",
#               "my-text-component-id.text": "Hello {John}!",
#               "my-image-component-id.src": "https://my-blog.com/my-image.jpg"
#             }
#         }'


def render_meme(img_source: str, text: str) -> utils.ResponseResult:
    header = {"X-API-KEY": renderio_api_key}
    data = {
        "template": "eager-kangaroos-snore-honestly-1305",
        "data": {
            "IMAGE.src": img_source,
            "TEXT.text": text
        }
    }
    url = "https://get.renderform.io/api/v2/render"
    return utils.send_post_json(url, data, header)


def do_exercise() -> None:
    auth_token = utils.get_auth_token_or_exit(exercise)
    exercise_response = utils.get_exercise_info_or_exit(auth_token, exercise)
    pp.pprint(exercise_response.result)
    img_source = exercise_response.result["image"]
    text = exercise_response.result["text"]

    response = render_meme(img_source, text)
    pp.pprint(response)
    if not response.is_valid_status():
        print("FATAL invalid response")
        exit(1)

    answer = response.result["href"]
    utils.send_solution_or_exit(auth_token, answer)


if __name__ == '__main__':
    print("START")
    do_exercise()
    print("END")
