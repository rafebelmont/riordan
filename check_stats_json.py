from bot_functions import arr_min_names
from bot_functions import valid_stats
import json

def check_integrity():
    with open('stats.json', 'r') as file:
        stats_check = json.load(file)
    
    problems=[]
    for name in arr_min_names:
        try:
            if stats_check[name].keys() == valid_stats:
                print(f'Creature {name} is OK.')
        except:
            problems.append(name)
            print(f'Problem with creature {name}.')
    if problems == []:
        print('Stats.json looks fine.')

check_integrity()
