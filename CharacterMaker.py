
import re
from typing import List
from GptHandler import gptCall
from CharacterClass import Character


promptTags="standing, facing camera, full body, vertical, solo, detailed"
traitListDatable = "tsundere, bakadere, bocchandere, bodere, dandere, deredere, hajidere, himedere, hiyakasudere, kamidere, yandere, nemuidere"
traitListDatableParent="Nurturing, Overprotective, Authoritative, Perfectionist, Helicopter, Laissez-faire, Supportive, Strict, UnconditionaLove, Sacrificing, Abusive, Neglectful, Unloving, Unsupportive"
relationList = "friend, family, datable, momOfDatable, dadOfDatable, siblingOfDatable"

class Player:
    def __init__(self, name: str, age: int, gender: str = None, sexuality: str = None, walletBal: int = 0, inventory: List[str] = [], relationships: List[str] = []):
        self.name = name
        self.age = age
        self.gender = gender
        self.sexuality = sexuality
        self.walletBal = walletBal
        self.relationships = relationships
        self.inventory = inventory

    def __repr__(self):
        return f"Player:[name: {self.name}, age: {self.age}, gender: {self.gender}, sexuality: {self.sexuality}, walletBal: {self.walletBal}, relationships: [{str(self.relationships)}], inventory: [{str(self.inventory)}]]"

    def dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "sexuality": self.sexuality,
            "walletBal": self.walletBal,
            "relationships": self.relationships,
            "inventory": self.inventory
        }

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
    player = Player("Shmarples", 18, "male", "heterosexual")
    prompt = f"""
    "You are an AI with the purpose of generating a new character for a dating sim."
    REQUIREMENTS:
    1. Characters must have one or more tropes from this list [{tropes}]
        a. make sure the tropes selected don't conflict with each other and relate to the character description
    2. Characters MUST be compatible with {player.gender} players, aged {player.age}, and {player.sexuality}
    2. If the character is female, she must have a breast size from this list [small, medium, large]
    3. If a variable is already specified in this list [{presetTraits}], you don't need to generate it (if the list is empty generate everything)
    4. You MUST create an outfit for the character specifying each of the relevant variables (as shown in response format)
        a. specify things that relate to the outfit even if they aren't visible from the outside, underwear for example
        b. when specifying something with a specific color, you MUST include what it is. For example, "red hair, blue eyes" instead of "red, blue"
    5. Height must be specified in inches
    6. IMPORTANT: all characters must be over 18 and not in high school

    RESPONSE FORMAT:
    name="character name":
            characterType="datable"
            description="description"
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
                    socks="outfit socks if applicable"
                    shoes="outfit shoes if applicable"
                    head="outfit headware if applicable"
                    face="outfit faceware if applicable"
                    bra="outfit bra if applicable"
                    underwear="outfit underwear"
                    neckwear="outfit neckwear if applicable"
                    ring="outfit ring if applicable"
                    wristware="outfit wristware if applicable"
                    waistware="outfit waistware if applicable"
                    ankleware="outfit ankleware if applicable"
        """
    
    response = gptCall(prompt, temperature=0.82)
    character = Character()
    character.parseText(response)
    
    return player, character

def genStartImg(character: Character):
    from ImgGen import genStanding
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

if __name__ == "__main__":
    player = Player("Shmarples", 18, "male", "heterosexual")
    player, character = makeCharacter(player, "datable", "description=\"A seductive personal assistant with a flirty personality, she's in love with robert but is too embarrased to say it\"")
    print(str(character))
    print(repr(character))