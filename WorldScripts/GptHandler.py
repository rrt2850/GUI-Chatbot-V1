import os
import subprocess
import time
import json
from typing import Dict, List

from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY", "")

temperature = float(os.getenv("GPT_TEMP", "0.6"))
model = os.getenv("GPT_MODEL", "text-davinci-003")
if "gpt-4" in model.lower():
    print(
        "\033[91m\033[1m"
        + "\n*****USING GPT-4. POTENTIALLY EXPENSIVE. MONITOR YOUR COSTS*****"
        + "\033[0m\033[0m"
    )

def gptCall(
    prompt: str,
    model: str = model,
    temperature: float = temperature,
    messages: str = None,
    max_tokens: int = 2000,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    top_p: float = 1.0,
):
    while True:
        try:
            if not model.startswith("gpt-"):
                # Use completion API
                response = openai.Completion.create(
                    engine=model,
                    prompt=prompt,
                    temperature=1,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    n=1
                )
                return response.choices[0].text.strip()
            else:
                # Use chat completion API
                if not messages: messages = [{"role": "system", "content": prompt}]
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty,
                    n=1,
                    stop=None,
                )

                with open("summary.json", "w") as outfile:
                    json.dump(response.choices, outfile)
                return response.choices[0].message.content.strip()
        except openai.error.RateLimitError:
            print(
                "The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again."
            )
            time.sleep(10)  # Wait 10 seconds and try again
        else:
            break

