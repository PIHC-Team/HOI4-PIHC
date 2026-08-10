from hoi4dev import *
import numpy as np

TEMPLATE = {
    "every_possible_country": {
        "limit": {
            "is_pony_country": True,
            "is_dynamic_country": False,
            "is_blank_country": False
        },
        "random_list": {
            "seed": "random",
            "1": {
                "generate_character": {
                    "token_base": "CHARACTER_GENERIC_RANDOM_<TOKEN>",
                    "advisor": {
                        "allowed": {
                            "always": True
                        }
                    },
                    "gender": "male"
                }
            },
            "5": {
                "generate_character": {
                    "token_base": "CHARACTER_GENERIC_RANDOM_<TOKEN>_FEMALE",
                    "advisor": {
                        "allowed": {
                            "always": True
                        }
                    },
                    "gender": "female"
                }

            }
        }
    }
}

N_COUNTRIES = 67
HASH_MOD = 1004535809

def get_all_political_advisors(gender):
    return [[
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_002_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_003_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_008_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_009_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_010_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_011_portrait",
    ], [
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_001_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_004_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_005_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_006_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_007_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_012_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_013_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_014_portrait",
        "GFX_RANDOM_CHARACTER_PONY_POLITICAL_015_portrait",
    ]][gender=='female']

def add_random_pony_characters():
    data = LoadJson("./resources/random_advisors.json")
    male_portraits = get_all_political_advisors('male')
    female_portraits = get_all_political_advisors('female')
    def add_advisor(scope, token, traits, advisor_data, advisors, identifier):
        template = deepcopy(TEMPLATE)
        if scope != "all":
            template[scope] = deepcopy(TEMPLATE["every_possible_country"])
            del template["every_possible_country"]
            del template[scope]["limit"]
        else:
            scope = "every_possible_country"
        tag = f"{token}_{scope[1:] if scope!='every_possible_country' else 'ALL'}_{identifier}"
        template[scope]["random_list"]["1"]["generate_character"]["token_base"] = \
        template[scope]["random_list"]["1"]["generate_character"]["token_base"].replace("<TOKEN>", tag)
        template[scope]["random_list"]["1"]["generate_character"]["advisor"] |= advisor_data | {"traits": traits}

        template[scope]["random_list"]["5"]["generate_character"]["token_base"] = \
        template[scope]["random_list"]["5"]["generate_character"]["token_base"].replace("<TOKEN>", tag)
        template[scope]["random_list"]["5"]["generate_character"]["advisor"] |= advisor_data | {"traits": traits}
        if advisor_data['slot'] == 'political_advisor':
            template[scope]["random_list"]["1"]["generate_character"]['portraits'] = {"army": {"small": male_portraits[int(MD5(identifier)%len(male_portraits))]+"_small"}}
            template[scope]["random_list"]["5"]["generate_character"]['portraits'] = {"army": {"small": female_portraits[int(MD5(identifier)%len(male_portraits))]+"_small"}}
        return merge_dicts([advisors, template], d=True)
    for id, generation in enumerate(data, 1):
        for scope, count in generation['dist'].items():
            advisors = dict()
            if count == 'all':
                for i, (token, traits, advisor_data) in enumerate(generation['gen']):
                    advisors = add_advisor(scope, token, traits, advisor_data, advisors, identifier=f"{id:02d}_{i:03d}")
            elif count > 0:
                random_rows = np.random.choice(range(len(generation['gen'])), count, replace=False if count<=len(generation['gen']) else True)
                for i, row_id in enumerate(random_rows):
                    token, traits, advisor_data = generation['gen'][row_id]
                    advisors = add_advisor(scope, token, traits, advisor_data, advisors, identifier=f"{id:02d}_{i:03d}")
            if advisors:
                SaveJson(advisors, f"./resources/copies/data/history/general/{id:02d}_pihc_{scope if scope!='all' else 'generic'}_advisors.json", indent=4)
    
    np.random.seed(42)
    data = LoadJson("./resources/random_corps_commanders.json")
    def add_corps_commander(scope, quality, corp_commanders_data, identifier):
        if scope == 'all':
            scope = 'every_possible_country'
        token_base = f"CHARACTER_GENERIC_RANDOM_CORPS_COMMANDER_{scope if scope!='every_possible_country' else 'ALL'}_{identifier}"
        generate_character = {
            "generate_character": {
                "token_base": token_base
            } | GetRandomCorpsCommander(quality=quality, seed=MD5(token_base)%HASH_MOD)
        }
        male_character = deepcopy(generate_character)
        male_character['generate_character']['gender'] = "male"
        female_character = deepcopy(generate_character)
        female_character['generate_character']['gender'] = "female"
        return merge_dicts([corp_commanders_data, {
            scope: ({
                "limit": {
                    "is_pony_country": True,
                    "is_dynamic_country": False,
                    "is_blank_country": False,
                }
            } if scope=='every_possible_country' else {}) | {
                "random_list": {
                    "seed": "random",
                    "1": male_character,
                    "5": female_character
                }
            }
        }], d=True)
        
    for id, generation in enumerate(data, 1):
        for scope, count in generation['dist'].items():
            corp_commanders = dict()
            if count > 0:
                qualities = sum([[int(k)]*v for k, v in generation['gen'].items()], [])
                for i in range(count):
                    quality = int(np.random.choice(qualities))
                    corp_commanders = add_corps_commander(scope, quality, corp_commanders, identifier=f"{id:02d}_{i:03d}")
                SaveJson(corp_commanders, f"./resources/copies/data/history/general/{id:02d}_pihc_{scope}_corp_commanders.json", indent=4)

    np.random.seed(42)
    specializations = list(LoadJson("./resources/copies/data/common/special_projects/specialization/specializations.json").keys())
    data = LoadJson("./resources/random_scientists.json")
    def add_scientist(scope, traits, mode, scientists_data, identifier):
        if scope == 'all':
            scope = 'every_possible_country'
        token_base = f"CHARACTER_GENERIC_RANDOM_SCIENTIST_{scope if scope!='every_possible_country' else 'ALL'}_{identifier}"
        generate_character = GetRandomScientist(mode=mode, specializations_pool=specializations, traits_pool=traits, seed=MD5(token_base)%HASH_MOD)
        male_character = deepcopy(generate_character)
        male_character['generate_scientist_character']['gender'] = "male"
        female_character = deepcopy(generate_character)
        female_character['generate_scientist_character']['gender'] = "female"
        return merge_dicts([scientists_data, {
            scope: ({
                "limit": {
                    "is_pony_country": True,
                    "is_dynamic_country": False,
                    "is_blank_country": False,
                }
            } if scope=='every_possible_country' else {}) | {
                "random_list": {
                    "seed": "random",
                    "1": male_character,
                    "5": female_character
                }
            }
        }], d=True)
        
    for id, generation in enumerate(data, 1):
        for scope, count in generation['dist'].items():
            scientists = dict()
            if count == 'all':
                for i, (traits, mode) in enumerate(generation['gen']):
                    scientists = add_scientist(scope, traits, mode, scientists, identifier=f"{id:02d}_{i:03d}")
            elif count > 0:
                random_rows = np.random.choice(range(len(generation['gen'])), count, replace=False if count<=len(generation['gen']) else True)
                for i, row_id in enumerate(random_rows):
                    traits, mode = generation['gen'][row_id]
                    scientists = add_scientist(scope, traits, mode, scientists, identifier=f"{id:02d}_{i:03d}")
            if scientists:
                SaveJson(scientists, f"./resources/copies/data/history/general/{id:02d}_pihc_{scope if scope!='all' else 'generic'}_scientists.json", indent=4)