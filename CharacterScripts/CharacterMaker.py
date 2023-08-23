"""
Author:         Robert Tetreault (rrt2850)
Filename:       CharacterMaker.py
Description:    A script that uses OpenAI's GPT-3.5 API to generate a character for the game.
Note:           This script is currently not used because the technology wasn't advanced enough to
                match the quality of the characters I wanted to generate at the time, but now that
                we can train our own 3.5 turbo models, I might revisit this idea.
"""

import os

import openai
from CharacterScripts.CharacterClass import Character, Player

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

promptTags="standing, facing camera, full body, vertical, solo, detailed"
traitListDatable = "tsundere, bakadere, bocchandere, bodere, dandere, deredere, hajidere, himedere, hiyakasudere, kamidere, yandere, nemuidere"
traitListDatableParent="Nurturing, Overprotective, Authoritative, Perfectionist, Helicopter, Laissez-faire, Supportive, Strict, UnconditionaLove, Sacrificing, Abusive, Neglectful, Unloving, Unsupportive"
relationList = "friend, family, datable, momOfDatable, dadOfDatable, siblingOfDatable"


def makeCharacter(
    player: Player=Player("Robert", 21, "male", "heterosexual"), tropes: str = traitListDatable, presetTraits: str = ""
):
    promptOld = f"""
"You are an AI with the purpose of generating a new character for a dating sim. You must follow the REQUIREMENTS below while fitting the JSON RESPONSE FORMAT."
REQUIREMENTS:
make sure to create a personality for the character, go into a moderate amount of detail with it. For example: "lucy is a shy girl with a good heart, she is very kind and caring but has trouble expressing herself"
make sure to create a backstory for the character that relates to the characters personality and tropes, possibly explaining them. feel free to get creative with this, creating a backstory that is interesting and unique that the character can talk about.
Characters must have one or more tropes that relate to their personality and backstory. make sure the tropes selected make sense and don't conflict with each other.
Characters MUST be compatible with {player.gender} players, aged {player.age}, and {player.sexuality}
If the character is female, she must have a breast size from this list [small, medium, large]
You MUST create an outfit for the character specifying each of the relevant variables (as shown in response format)
include everything that you include in the outfit summary, when specifying something with a specific color, you MUST include what it is. For example, "red hair, blue eyes" instead of "red, blue". 
include only visible outfit parts in the summary but include ALL outfit parts in the outfit variables make sure panties and bras are separate variables
Height must be specified in inches
IMPORTANT: all characters must be over 18 and not in high school

use this description of the player when generating the character: {player.lore}

respond exactly as shown in the response format without modifying the spacing, capitalization, or quotation types
JSON RESPONSE FORMAT:
{{
    "name":"character name",
    "age":"character age",
    "gender":"character gender",
    "personality":"character personality",
    "backstory":"character backstory",
    "tropes":"character tropes separated by commas",
    "sexuality":"character sexuality",
    "characterType":"datable",
    "height":"character height",
    "breastSize":"character breast size",
    "hairStyle":"character hair style",
    "hairColor":"character hair color",
    "eyeColor":"character eye color",
    "skinColor":"character skin color",
    "outfitSummary":"character outfit summary",
    "outfit":{{
        "top":"character outfit top",
        "bottom":"character outfit bottom",
        "socks":"character outfit socks",
        "shoes":"character outfit shoes",
        "head":"character outfit headwear",
        "face":"character outfit facewear",
        "bra":"character outfit bra",
        "underwear":"character outfit underwear",
        "neck":"character outfit neckwear",
        "ring":"character outfit ring",
        "wristware":"character outfit wristware",
        "waistware":"character outfit waistware",
        "ankleware":"character outfit ankleware"
    }}
}}
        """

    prompt = f"""
You are an AI with the purpose of generating a new character for a dating sim. follow the REQUIREMENTS below while filling THE ENTIRE RESPONSE TEMPLATE. Your response must exactly fit the or there will be parsing errors.

REQUIREMENTS:
ALL variables in the response template must be filled out
use moderate detail when making the personality For example: "lucy is a shy girl with a good heart, she is very kind and caring but has trouble expressing herself"
make a backstory that loosely relates to the characters personality. create a backstory that is interesting and unique while still concise.
create tropes based on the personality, the tropes selected must make sense and not conflict with each other.
Characters MUST be compatible with {player.gender} players, aged {player.age}, and {player.sexuality} for example, if the player is male and heterosexual generate a female character that is heterosexual or bisexual
If the character is female, she must have a breast size from this list [small, medium, large]
when specifying something with a specific color, include what it is. For example, "red hair, blue eyes" instead of "red, blue". 
Height must be specified in inches
IMPORTANT: all characters must be over 18 and not in high school
IMPORTANT: match the formatting of the response template EXACTLY, including the spacing, capitalization, and quotation types

RESPONSE TEMPLATE:
{{
    "name":"character name",
    "age":"character age",
    "gender":"character gender",
    "sexuality":"character sexuality",
    "characterType":"datable",
    "height":"character height",
    "breastSize":"character breast size",
    "hairStyle":"character hair style",
    "hairColor":"character hair color",
    "eyeColor":"character eye color",
    "skinColor":"character skin color",
    "personality":"character personality",
    "backstory":"character backstory",
    "tropes":"character tropes separated by commas",
}}
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
    
    return player, character

