import bot_functions
import time
import json

regenerate_all = False #change this to True if you want to grab all card stats again
number_of_minis = len(bot_functions.arr_min_names)
counter = 1

start = time.perf_counter()

with open('stats.json', 'r') as file:
    stats_check = json.load(file)

skipped = 0
for name in bot_functions.arr_min_names:
    print(f'Getting stats for {name}.')
    ratio = counter/number_of_minis*100
    print(f'Process is {ratio:.2f}% done.')
    counter = counter + 1
    if regenerate_all == True:
        try:
            bot_functions.get_card_stats_online(name)
        except:
            print(f'Some problem occured with {name}. Skipping it.')
            skipped = skipped + 1
            continue
    else:
        try:
            #stats_check[name]
            if stats_check[name].keys() == bot_functions.valid_stats:
                continue
            else:
                try:
                    bot_functions.get_card_stats_online(name)
                except:
                    print(f'Some problem occured with {name}. Skipping it.')
                    skipped = skipped + 1
                    continue
        except:
            try:
                bot_functions.get_card_stats_online(name)
            except:
                print(f'Some problem occured with {name}. Skipping it.')
                skipped = skipped + 1
                continue

        
end=time.perf_counter()

Elapsed = end - start

print(f'Elapsed time was {Elapsed} seconds. Number of skipped creatures: {skipped}.')