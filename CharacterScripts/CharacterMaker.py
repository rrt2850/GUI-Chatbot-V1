"""
messages = [
    {"role": "system", "content": prompt}
]

response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        max_tokens=2000,
        top_p=1,
        frequency_penalty=1.8,
        presence_penalty=1.8,
    )

response = response.choices[0].message.content
print(f"Response: \n\033[1;36m{response}\033[0m")


character = Character()
character.parseText(response)

"""
