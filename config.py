import json


def load_config(config_file="config.json"):
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


default_config = {
    "auto_print_hand_sum": True,
    "dealer_hits_on_soft_17": True,
    "insurance_allowed": True,
    "num_decks": 6,
    "reshuffle_threshold": 15,
    "show_hints": True,
    "starting_amount": 1000,
}

with open("config.json", "w", encoding="utf-8") as f:
    json.dump(default_config, f, indent=4)
