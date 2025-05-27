import bot_functions
import time

regenerate_all = False #change this to True if you want to grab all card again
number_of_minis = len(bot_functions.arr_min_names)
counter = 1
skipped = 0

start = time.perf_counter()

for the_card_name in bot_functions.arr_min_names:
    print(f'Getting stats for {the_card_name}.')
    ratio = counter/number_of_minis*100
    print(f'Process is {ratio:.2f}% done.')
    counter = counter + 1
    try:
        bot_functions.get_card(the_card_name, regenerate=regenerate_all)
    except:
        print(f'Problem getting card for creature {the_card_name}. Skipping it for now.')
        skipped = skipped + 1

end=time.perf_counter()

Elapsed = end - start

print(f'Elapsed time was {Elapsed} seconds. Number of skipped creatures: {skipped}.')