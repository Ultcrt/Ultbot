import requests

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/91.0.4472.164 Safari/537.36 Edg/91.0.864.71'}


def exchange_list(json_resp):
    res_str = "币种简写对照表：\n"
    for item in json_resp.items():
        res_str += item[0] + " => " + item[1]["name"] + "\n"
    return res_str


def get_exchange_rates():
    url = "https://api.coingecko.com/api/v3/exchange_rates"

    response = requests.get(url, headers=headers, timeout=5)

    return response.json()["rates"]