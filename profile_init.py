import json


def auto_stat(value):
    return int(value) if value is not None else 60


def init(user_id, rp_id, template_match, eng_name, gen_name):
    tm = template_match
    profile_data = {
                    "player_id": user_id,
                    "nominative": tm[1],
                    "genitive": gen_name,
                    "gender": tm[2].lower(),
                    "dominant hand": tm[3].lower() if tm[3] is not None else "правая",

                    "strength": auto_stat(tm[4]),
                    "agility": auto_stat(tm[5]),
                    "magic": (magic := auto_stat(tm[6])),
                    "charisma": auto_stat(tm[7]),
                    "endurance": (endurance := auto_stat(tm[8])),
                    "intelligence": auto_stat(tm[9]),
                    "perception": auto_stat(tm[10]),

                    "luck": 60,

                    "health": endurance*10,
                    "stamina": endurance*5,
                    "mana": magic*10,

                    "right hand": [],
                    "left hand": [],
                    "waist": {},
                    "clothes": [],
                    "skills": [],
                    "inventory": {},

                    "ready action": "",
                    "RP_id": rp_id
                }
    with open(f'heroes/{eng_name}.json', 'x', encoding="utf-8") as json_profile:
        json.dump(profile_data, json_profile, indent=4, ensure_ascii=False)
