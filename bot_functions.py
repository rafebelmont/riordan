from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from thefuzz import fuzz
from thefuzz import process

import time
import json
import os
import math

from PIL import Image

from min_names import *

cards_folder_prefix = 'cards/' 
website = 'https://ddmwarbands.altervista.org/'
valid_stats = {"points", "epic-points", "faction", "level", "speed", "AC", "HP", "epic-level", "epic-speed", "epic-AC", "epic-HP"}
factions_list ={"CG", "LG/CG", "LG", "LG/LE", "LE", "CG/CE", "CE", "LE/CE", "Any"}

class BotBrowser:
    instances=[]
    def __init__(self):
        options = webdriver.FirefoxOptions()
        #options.add_argument('--headless') #this for a browser window to not appear when running the code
        #options.add_argument('--no-sandbox')
        self.driver = webdriver.Firefox(options=options)
        self.driver.get(website)
        self.driver.maximize_window()
        points_system_box = Select(self.driver.find_element(By.ID,'myPointSystem'))
        points_system_box.select_by_visible_text('Revised')
        BotBrowser.instances.append(self)

def give_browser():
    if BotBrowser.instances == []:
        browser = BotBrowser()
        return browser
    else:
        browser = BotBrowser.instances[0]
        return browser

def get_card_name(search_name: str):
    #check for aliases
    with open("aliases.json") as file:
        aliases = json.load(file)
    possible_alias, score = process.extractOne(search_name, aliases.keys())
    alias = possible_alias if score == 100 else None
    if alias != None:
        the_card_name = process.extractOne(aliases[alias], arr_min_names)[0]
    else:
        the_card_name = process.extractOne(search_name, arr_min_names)[0]
    return the_card_name

def get_card(search_name_arg: str, regenerate=False):
    
    #get closest match to search_name_arg
    search_name = search_name_arg
    the_card_name = get_card_name(search_name)
    

    #check if card jpg is already downloaded
    file_name_str_jpg = cards_folder_prefix+the_card_name+'.jpg'
    if os.path.exists(file_name_str_jpg) and regenerate==False:
        return file_name_str_jpg
    else:
        browser = give_browser()
        driver = browser.driver
    #we implement the search below
        creature_name_box = driver.find_element(By.ID, 'myName') 
        creature_name_box.clear()
        creature_name_box.send_keys(the_card_name)
        #creature_name_box.send_keys(Keys.DOWN) #since we lookup for the correct name outside WBbuilder, there is no need for this
        creature_name_box.send_keys(Keys.ENTER)

    # a little wait time to let the results load
        time.sleep(2.5)

        cards = driver.find_elements(By.CSS_SELECTOR, '[class="card"]') 

    # we need to get the card name which is the closest to our search_name variable
        card_titles=[]
        for card in cards:
            card_title = card.find_element(By.CSS_SELECTOR,'b')
            card_titles.append(card_title)
        #the_card_name = process.extractOne(search_name, [card_title.text for card_title in card_titles])[0]

    # selecting the correct card. Note that we check for 'epicness'
        for card in cards:

            card_title = card.find_element(By.CSS_SELECTOR,'b')
            if card_title.text == the_card_name and card.find_elements(By.CSS_SELECTOR,'[class="background-epic"]') == []:
                the_card = card
                break
            else:
                if card_title.text == the_card_name:
                    the_card = card

    #screenshotting the result and conversion to jpg
        file_name_str = cards_folder_prefix+the_card_name+'.png'
        the_card.screenshot(file_name_str)
        file_name_str_jpg = convert_to_jpg(file_name_str, the_card_name)

        return file_name_str_jpg
    
def convert_to_jpg(img_path: str, the_card_name: str):
    img_png = Image.open(img_path)
    file_name_str_jpg = cards_folder_prefix+the_card_name+'.jpg'
    card_width, card_height = img_png.size
    new_card_width = 450
    new_card_height = math.floor((new_card_width/card_width)*card_height)
    img_png_rgb = img_png.convert('RGB')
    resized_img = img_png_rgb.resize((new_card_width,new_card_height))
    resized_img.save(file_name_str_jpg)
    os.remove(img_path)
    return file_name_str_jpg

def get_card_stat(the_card_name: str, stat: str):
    
    if stat not in valid_stats:
        raise ValueError("Stat must be one of %r." % valid_stats)

    with open('stats.json', 'r') as file:
        stats = json.load(file)
        try:
            return stats[the_card_name][stat]
        except KeyError:
            get_card_stats_online(the_card_name)
   
    return stats[the_card_name][stat]

def get_card_stats_online(the_card_name):

    with open('stats.json', 'r') as file:
        stats = json.load(file)

    browser = give_browser()
    driver = browser.driver
    creature_name_box = driver.find_element(By.ID, 'myName') 
    creature_name_box.clear()
    creature_name_box.send_keys(the_card_name)
    creature_name_box.send_keys(Keys.ENTER)

    time.sleep(1) #reducing this, since i think we do not need to wait a lot to grab stats, old value is 2.5

    cards = driver.find_elements(By.CSS_SELECTOR, '[class="card"]') 

    for card in cards:
        card_title = card.find_element(By.CSS_SELECTOR,'b')
        if card_title.text == the_card_name and card.find_elements(By.CSS_SELECTOR,'[class="background-epic"]') == []:
            if 'the_card_non_epic' in locals():
                continue
            else:
                the_card_non_epic = card
        else:
            if card_title.text == the_card_name:
                the_card_epic = card

    # getting "points"    
    try:
        points_str = the_card_non_epic.find_element(By.CSS_SELECTOR,'[class="points-non-epic"]').text
    except:
        points_str = "0\nPoints"
            
    points = int(points_str[:-7]) #this removes the '\nPoints' part of the string

    # getting "epic-points"
    try:
        points_str = the_card_epic.find_element(By.CSS_SELECTOR,'[class="points-epic"]').text
    except:
        points_str = "0\nPoints"
            
    epic_points = int(points_str[:-7][-3:]) #this removes the '\nPoints' and the 'EPIC\n' part of the string
    
    # getting "faction"
    try:
        faction = the_card_non_epic.find_element(By.CSS_SELECTOR, '[class="title2"]').text
    except:
        faction = the_card_epic.find_element(By.CSS_SELECTOR, '[class="title2"]').text
    
    # getting "left-stats" (Level, Speed, AC, HP)
    if "the_card_non_epic" in locals():
        left_stats_web_element_non_epic = the_card_non_epic.find_elements(By.CSS_SELECTOR, '[class="left-stat"]')
        level = int(left_stats_web_element_non_epic[0].text.strip('LEVEL\n'))
        speed = left_stats_web_element_non_epic[1].text.strip('SPEED\n') #speed has to be a string because flying is a thing
        ac = int(left_stats_web_element_non_epic[2].text.strip('AC\n'))
        hp = int(left_stats_web_element_non_epic[3].text.strip('HP\n'))
    else:
        level = 0
        speed = 0
        ac = 0
        hp = 0

    if "the_card_epic" in locals():
        left_stats_web_element_epic = the_card_epic.find_elements(By.CSS_SELECTOR, '[class="left-stat"]')
        level_epic = int(left_stats_web_element_epic[0].text.strip('LEVEL\n'))
        speed_epic = left_stats_web_element_epic[1].text.strip('SPEED\n') #speed has to be a string because flying is a thing
        ac_epic = int(left_stats_web_element_epic[2].text.strip('AC\n'))
        hp_epic = int(left_stats_web_element_epic[3].text.strip('HP\n'))
    else:
        level_epic = 0
        speed_epic = 0
        ac_epic = 0
        hp_epic = 0
    
    #updating stats.json
    dict = {the_card_name: {"points": points, "epic-points": epic_points, "faction": faction, "level": level, "speed": speed, "AC": ac, "HP": hp, "epic-level": level_epic, "epic-speed": speed_epic, "epic-AC": ac_epic, "epic-HP": hp_epic}}
    stats.update(dict)
    with open('stats.json', 'w') as file:
        json.dump(stats,file)

def build_warband(*args):
    total_points=0
    total_hp = 0
    dict = {}
    counter=1
    for arg in args:
        the_card_name = get_card_name(arg)
        points = get_card_stat(the_card_name, "points")
        hp = get_card_stat(the_card_name, "HP")
        total_points = total_points + points
        total_hp = total_hp + hp
        dict_entry = {counter: (the_card_name, points)}
        dict.update(dict_entry)
        counter = counter +1
    return dict, total_points, total_hp

def concat_cards(jpg_list):
    images = [Image.open(cards_folder_prefix+jpg) for jpg in jpg_list]
    number_of_cards=len(jpg_list)
    lines = math.ceil(number_of_cards/4)
    card_width = images[0].size[0]
    card_height = max([image.size[1] for image in images])
    height = lines*card_height
    if lines == 1:
        width = number_of_cards*card_width
    else:
        width = 4*card_width    
    the_image = Image.new('RGB', (width, height))
    counter = 1
    images.sort(key=lambda x: x.size[1], reverse = True) #this sorts the images list to cards with larger heights first
    for image in images:
        y_shift = math.floor((counter-1)/4)*card_height
        x_shift = ((counter-1) % 4)*card_width
        the_image.paste(image,(x_shift,y_shift))
        counter = counter + 1
    the_image.save('tmp/warband.jpg')
    return 'tmp/warband.jpg'

def look_for_minis(number_of_minis, faction: str, points_sum):
    return

def factions(faction_search_name: str):
    faction = process.extractOne(faction_search_name, factions_list)[0]
    tokens_list = faction.split("/")
    result ={"Any"}
    for alignment in factions_list:
        for token in tokens_list:
            if alignment.find(token) != -1:
                result.add(alignment)
    return result

def look_for_minis_with_stat(faction: str, stat: str, between_start, between_end):
    factions_wanted = factions(faction)
    dict = {}
    with open('stats.json','r') as file:
        stats = json.load(file)
    for mini in arr_min_names:
        try:
            if stats[mini][stat] <= between_end and stats[mini][stat] >= between_start:
                dict.update({mini: stats[mini][stat]})
        except:
            continue
    return dict

#Here we add all the 'interface' functions with the Discord bot:
def give_card(search_name: str, regenerate = False):
    file_name = get_card(search_name, regenerate)
    return file_name

def give_warband (*args):
    warband, total_points, total_hp = build_warband(*args)
    warband_list = []
    jpg_list = []
    for key, value in warband.items():
        creature_string = value[0]+f' ({value[1]})'
        creature_jpg = value[0]+'.jpg'
        warband_list.append(creature_string)
        jpg_list.append(creature_jpg)
    separator = ', '
    warband_string = separator.join(warband_list)
    warband_jpg = concat_cards(jpg_list)
    return warband_string, total_points, total_hp, warband_jpg

def add_alias(alias: str, search_name):
    the_card_name = process.extractOne(search_name, arr_min_names)[0]
    with open("aliases.json") as file:
        aliases = json.load(file)
    entry = {alias: the_card_name}
    aliases.update(entry)
    with open('aliases.json', 'w') as file:
        json.dump(aliases,file)
    return the_card_name