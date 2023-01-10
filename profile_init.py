import re
import json


def init(user_id, RP_id, new_profile_text, eng_name, gen_name):
    nom_name = new_profile_text[4:re.search(r'[\n.]', new_profile_text).start()].strip()
    gender_start = new_profile_text.find('Пол:')+4
    hand_start = new_profile_text.find('Ведущая рука:')+13
    gender = new_profile_text[gender_start: gender_start+8].strip()
    hand = new_profile_text[hand_start: hand_start+7].strip()
    stats = new_profile_text[new_profile_text.find('Статы:')+6:].strip().splitlines()
    values = [int(re.search(r'\d+', stat)[0]) for stat in stats]
    jp = {
                    "player_id": user_id,
                    "nominative": nom_name,
                    "genitive": gen_name,
                    "gender": gender.lower(),
                    "dominant hand": hand.lower(),

                    "strength": values[0],
                    "agility": values[1],
                    "magic": values[2],
                    "charisma": values[3],
                    "endurance": values[4],
                    "intelligence": values[5],
                    "perception": values[6],

                    "luck": 60,

                    "health": values[4]*10,
                    "stamina": values[4]*5,
                    "mana": values[2]*10,

                    "right hand": [],
                    "left hand": [],
                    "waist": {},
                    "clothes": [],
                    "skills": [],
                    "inventory": {},

                    "ready action": "",
                    "RP_id": RP_id+2000000000
                }
    with open(f'heroes/{eng_name}.json', 'x') as json_profile:
        json.dump(jp, json_profile, indent=4, ensure_ascii=False)
