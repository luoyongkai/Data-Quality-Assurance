import requests
import json
import time
from openai import OpenAI
from prompt.fact_check_prompt import baichuan_fact
def gpt(messages=[], system_prompt="", temperature=0.3):
    """
    :param messages: 用户输入信息
    :param system_prompt: 系统角色信息
    :param temperature: 温度
    :return: 模型返回信息
    """
    successful = 0
    while True:
        try:
            url = "http://xxx/v1/chat/completions"

            payload = json.dumps({
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": messages
                    }
                ],
                "temperature": temperature
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-xxx'

            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            gpt= json.loads(response.text)['choices'][0]['message']['content']
            successful = 1
            break
        except Exception as e:
            print(" - GPT Error - ", e)
            time.sleep(10)
            continue
    if successful == 0:
        return ""
    return gpt



def baichuan(messages=[], system_prompt="", temperature=0.3):
    """
    :param messages: 用户输入信息
    :param system_prompt: 系统角色信息
    :param temperature: 温度
    :return: 模型返回信息
    """
    successful = 0
    while True:
        try:
            url = "https://api.baichuan-ai.com/v1/chat/completions"

            payload = json.dumps({
                "model": "Baichuan4",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": messages
                    }
                ],
                "temperature": temperature
            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-xxx'

            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            baichuan= json.loads(response.text)['choices'][0]['message']['content']
            successful = 1
            break
        except Exception as e:
            print(" - GPT Error - ", e)
            time.sleep(10)
            continue
    if successful == 0:
        return ""
    return baichuan


def o1(messages=[], temperature=1):
    """
    o1模型不支持sys消息，以及tempereture需设置为1

    :param messages: 用户输入信息
    :param temperature: 温度
    :return: 模型返回信息
    """
    successful = 0
    while True:
        try:
            url = "http://xxx/v1/chat/completions"
            payload = json.dumps({
                "model": "gpt-4o",
                "messages": [{
                    "role": "user",
                    "content": messages
                    # "content": "Calculate the integral of 3x over the interval [1, 5]."
                }],
                "temperature": temperature

            })
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer sk-xxx'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            o1 = json.loads(response.text)['choices'][0]['message']['content']
            successful = 1
            break
        except Exception as e:
            print(" - GPT Error - ", e)
            time.sleep(10)
            continue
    if successful == 0:
        return ""
    return o1




client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.baichuan-ai.com/v1/",
)


def chat(messages_baichuan):
    messages = [
        {"role": "system", "content": baichuan_fact},
        {"role": "user", "content": messages_baichuan}
    ]
    completion = client.chat.completions.create(
        model="Baichuan4",
        messages=messages,
        temperature=0.3,
        stream=False,
        extra_body={
            "tools": [{
                "type": "web_search",
                "web_search": {
                    "enable": True,
                    "search_mode": "quality_first"
                }
            }]
        }

    )
    return completion.choices[0].message.content

