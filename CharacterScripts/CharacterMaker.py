import re
import sys
import os
from typing import List

import openai
from WorldScripts.GptHandler import gptCall
from CharacterScripts.CharacterClass import Character, Player

from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

promptTags="standing, facing camera, full body, vertical, solo, detailed"
traitListDatable = "tsundere, bakadere, bocchandere, bodere, dandere, deredere, hajidere, himedere, hiyakasudere, kamidere, yandere, nemuidere"
traitListDatableParent="Nurturing, Overprotective, Authoritative, Perfectionist, Helicopter, Laissez-faire, Supportive, Strict, UnconditionaLove, Sacrificing, Abusive, Neglectful, Unloving, Unsupportive"
relationList = "friend, family, datable, momOfDatable, dadOfDatable, siblingOfDatable"



def genStartImgPrompt(character: Character):
    prompt = f"""
        "You are an AI with the purpose of converting a character description into a form usable by stable diffusion. Follow these guidelines:
        1. Use the provided input template to create the results.
        2. Summarize visible traits from the description into 1-3 word statements.
        3. Exclude irrelevant data like name.
        4. If outfit parts aren't visible, exclude them from the positivePrompt and include them in the negativePrompt
        5. Use tags from https://danbooru.donmai.us/ when possible.
        6. Order your prompt by importance, for example, if a character is wearing a jacket put it before their shirt because it's above it
        7. IMPORTANT: If the character is female, ensure breast size is included in the positivePrompt as "[breastSize] breasts"
        8. IMPORTANT: when specifying something with a specific color, include them in the same comma separated statement. For example, "red hair, blue eyes"
        9. IMPORTANT: when separating attributes by chracteristics, make sure to specify what each attribute is. For example, "brown hair, long wavy hair" is better than "brown, long, wavy hair"
        10. IMPORTANT: Ensure both positivePrompt and negativePrompt are concise and have fewer than 70 tokens in length. Prioritize essential traits in the character's appearance.
        INPUT FORMAT:
        name="character name":
            description="description"
            backstory="backstory"
            height="height"
            gender="gender"
            breastSize="breast size"
            hairStyle="hair style"
            hairColor="hair color"
            eyeColor="eye color"
            skinColor="skin color"
            tropes="character tropes separated by commas"
            outfitSummary="outfit summary"
                    top="outfit top"
                    bottom="outfit bottom"
                    socks="outfit socks if applicable"
                    shoes="outfit shoes"
                    head="outfit headware if applicable"
                    face="outfit faceware if applicable"
                    bra="outfit bra if applicable"
                    underwear="outfit underwear"
                    neck="outfit neckwear if applicable"
                    ring="outfit ring if applicable"
                    wristware="outfit wristware if applicable"
                    waistware="outfit waistware if applicable"
                    ankleware="outfit ankleware if applicable"
        OUTPUT FORMAT (PROMPTS MUST BE <= 70 TOKENS):
        positivePrompt: "all visual traits to keep separated by ', '"
        negativePrompt: "all visual traits we don't want to see separated by ', '"
        INPUT:
        {character.toImg()}
    """
    try:
        response = gptCall(prompt,temperature=0.82)
        return response
    except:
        print("Error generating image prompt")
        return None

def makeCharacter(
    player: Player=None, tropes: str = traitListDatable, presetTraits: str = ""
):
    player = Player("Robert", 21, "male", "heterosexual")
    prompt = f"""
    "You are an AI with the purpose of generating a new character for a dating sim. You must follow the REQUIREMENTS below while fitting the RESPONSE FORMAT."
    REQUIREMENTS:
    make sure to create a personality for the character, go into a moderate amount of detail with it. For example: "lucy is a shy girl with a good heart, she is very kind and caring but has trouble expressing herself"
    make sure to create a backstory for the character that relates to the characters personality and tropes, possibly explaining them. feel free to get creative with this, creating a backstory that is interesting and unique that the character can talk about.
    Characters must have one or more tropes that relate to their personality and backstory. make sure the tropes selected make sense and don't conflict with each other.
    Characters MUST be compatible with {player.gender} players, aged {player.age}, and {player.sexuality}
    If the character is female, she must have a breast size from this list [small, medium, large]
    If a variable is already specified in this list [{presetTraits}], you don't need to generate it (if the list is empty generate everything)
    You MUST create an outfit for the character specifying each of the relevant variables (as shown in response format)
    include everything that you include in the outfit summary, when specifying something with a specific color, you MUST include what it is. For example, "red hair, blue eyes" instead of "red, blue". 
    include only visible outfit parts in the summary but include ALL outfit parts in the outfit variables make sure panties and bras are separate variables
    Height must be specified in inches
    IMPORTANT: all characters must be over 18 and not in high school

    use this description of the player when generating the character: {player.lore}
    RESPONSE FORMAT:
    name="character name":
            characterType="datable"
            personality="personality"
            backstory="backstory"
            age="age"
            gender="gender"
            sexuality="sexuality"
            height="height"
            breastSize="breast size"
            hairStyle="hair style"
            hairColor="hair color"
            eyeColor="eye color"
            skinColor="skin color"
            tropes="character tropes separated by commas"
            outfitSummary="outfit summary"
                    top="outfit top"
                    bottom="outfit bottom"
                    socks="outfit socks"
                    shoes="outfit shoes"
                    head="outfit headware"
                    face="outfit faceware"
                    bra="outfit bra"
                    underwear="outfit underwear"
                    neckwear="outfit neckwear"
                    ring="outfit ring"
                    wristware="outfit wristware"
                    waistware="outfit waistware"
                    ankleware="outfit ankleware"
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

def genStartImg(character: Character):
    from ..ImageGen.ImgGen import genStanding
    prompts = genStartImgPrompt(character)
    print(f"Image prompts generated: \n\033[1;36m{prompts}\033[0m")

    pattern = r'(\w+)\s*=\s*"([^"]*)"'
    matches = re.finditer(pattern, prompts)

    filename = ""
    posVals = []
    negVals = []

    for match in matches:
        valueType, value = match.groups()
        if valueType == "positivePrompt":
            posVals.append(value)
        elif valueType == "negativePrompt":
            negVals.append(value)

    print(f"values: {posVals}")
    print(f"negVals: {negVals}")
    genStanding(filename, posVals, negVals)
    #command = f'{activate_path} activate {conda_env_name} && cd {imgGenDir} && python drawInterface.py "{names_str}" "{values_str}" "{negVals_str}"'
    #subprocess.check_call(command, shell=True)"""
