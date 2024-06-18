import random
import HSZC
import pprand

natures = ['Hard', 'Lonely', 'Brave', 'Adamant', 'Naughty', 'Bold', 'Docile', 'Relaxed', 'Impish', 'Lax', 'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive', 'Modest', 'Mild', 'Quiet', 'Bashful', 'Rash', 'Calm', 'Gentle', 'Sassy', 'Careful', 'Quirky']

trigger_flavs = []
trigger_flavs.append([0, 0.2200264, 0.2317442, 0.2556874, 0.292542])
trigger_flavs.append([0.1400924, 0, 0.2246866, 0.2827856, 0.3524354])
trigger_flavs.append([0.129346, 0.1736402, 0, 0.30366, 0.3933534])
trigger_flavs.append([0.1165784, 0.1695108, 0.2416138, 0, 0.472297])
trigger_flavs.append([0.0871222, 0.1561002, 0.2766238, 0.4801538, 0])

def get_odds_of_rate(rate, current_flav, throw_flav):
    '''FOR DETERMINING THE ODDS OF GETTING A ROLL ON THE FIRST TURN'''
    # IF current_flav = -1 never trigger the forced throw
    pprand.blockPrint()
    odds_of_trigger = pprand.pp_rand_variance(100, 0, 79)
    if current_flav == -1:
        odds_of_trigger = 0
    pprand.enablePrint()
    rand_odds_of_flav_yum = 4/25 * (1 - odds_of_trigger)
    rand_odds_of_flav_yuck = 4/25 * (1 - odds_of_trigger)
    rand_odds_of_flav_fine = (25 - 8)/25 * (1 - odds_of_trigger)
    # 0 SPICY, 1 SOUR, 2 SWEET, 3 DRY, 4 BITTER
    if current_flav >= 0 and current_flav != throw_flav:
        trigger_odds_of_flav_yuck = odds_of_trigger * (trigger_flavs[current_flav][throw_flav])
        trigger_odds_of_flav_fine = odds_of_trigger * (1 - trigger_flavs[current_flav][throw_flav])
        trigger_odds_of_flav_yum = 0
    elif current_flav >=0 :
        trigger_odds_of_flav_yuck = 0
        trigger_odds_of_flav_fine = 0
        trigger_odds_of_flav_yum = 1 * odds_of_trigger
    else:
        trigger_odds_of_flav_yuck = 0
        trigger_odds_of_flav_fine = 0
        trigger_odds_of_flav_yum = 0        
    if rate == 0:
        return trigger_odds_of_flav_fine + rand_odds_of_flav_fine
    if rate == 1:
        return rand_odds_of_flav_yum + trigger_odds_of_flav_yum
    if rate == 3:
        return rand_odds_of_flav_yuck + trigger_odds_of_flav_yuck

def get_odds_yum_2(current_flav, throw_flav):
    # GET ODDS OF FAILING ROLL 1 (IGNORED)
    fail_odds = get_odds_of_rate(3, current_flav, throw_flav) * 0.85    
    if current_flav == -1:
        suc_odds = 1/4
        f_odds = 3/4
    else:
        # GET ODDS OF SUCCESS ROLL 2
        suc_odds = 0.8 + (4/25) * 0.2
        f_odds = 1 - suc_odds
    return (suc_odds * fail_odds, f_odds * fail_odds)

def get_catch_odds(cr, current_flav, throw_flav=0, extra_throw=0):
    pprand.blockPrint()
    odds_of_trigger = pprand.pp_rand_variance(100, 0, 79)
    pprand.enablePrint()    
    if current_flav == "SYNC_ONLY":
        odds_of_0 = (0.5 + 0.5 * (25 - 8)/25) * 0.85
        odds_of_1 = (0.5 * (1-((25 - 4)/25))) * 0.85
        odds_of_3 = (0.5 * (1-((25 - 4)/25))) * 0.85
    elif current_flav == "COMPLEX":
        # 0 = NEUTRAL, 1 = LIKED 2 = DISLIKED
        odds_of_0 = (odds_of_trigger + (1-odds_of_trigger) * (25 - 8)/25) * 0.85
        odds_of_1 = ((1-odds_of_trigger) * (1-((25 - 4)/25))) * 0.85
        odds_of_3 = ((1-odds_of_trigger) * (1-((25 - 4)/25))) * 0.85
    elif current_flav == "SYNC_COMPLEX":
        odds_of_0 = (odds_of_trigger + (1-odds_of_trigger) * 0.5 + (1-odds_of_trigger) * 0.5 * (25 - 8)/25) * 0.85
        odds_of_1 = ((1-odds_of_trigger) * 0.5 * (1-((25 - 4)/25))) * 0.85
        odds_of_3 = ((1-odds_of_trigger) * 0.5 * (1-((25 - 4)/25))) * 0.85     
    else:
        odds_of_0 = get_odds_of_rate(0, current_flav, throw_flav) * 0.85
        odds_of_1 = get_odds_of_rate(1, current_flav, throw_flav) * 0.85
        odds_of_3 = get_odds_of_rate(3, current_flav, throw_flav) * 0.85
    s0 = HSZC.pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, cr, 0)[0]
    s1 = HSZC.pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, cr, 1)[0]
    s3 = HSZC.pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, cr, 3)[0]
    odds_of_success_0 = s0 * odds_of_0
    odds_of_success_1 = s1 * odds_of_1
    odds_of_success_3 = s3 * odds_of_3
    if extra_throw == 1:
        odds_of_success_3 = get_odds_yum_2(current_flav, throw_flav)[0] * 0.85 *  s0 + get_odds_yum_2(current_flav, throw_flav)[1] * 0.85 * s1
    return odds_of_success_0 + odds_of_success_1 + odds_of_success_3
import time
def rand_table():
    tbl = []
    for i in range(0, 25):
        tbl.append(i)
    for i in range(0, 24):
        for j in range(i+1, 25):
            if random.randint(0,1) in (1, 1):
                k = tbl[i]
                tbl[i] = tbl[j]
                tbl[j] = k
    return(tbl)
    
spicy = [1, 2, 3, 4]
sour = [5, 7, 8, 9]
sweet = [10, 11, 13, 14]
dry = [15, 16, 17, 19]
bitter = [20, 21, 22, 23]

#Hated Flavours
spicyh = [5, 10, 15, 20]
sourh = [1, 11, 16, 21]
sweeth = [2, 7, 17, 22]
dryh = [3, 8, 13, 23]
bitterh = [4, 9, 14, 19]

flavors = [spicy, sour, sweet, dry, bitter]
flavors2 = [spicy, sour, sweet, dry, bitter]
flavorsh = [spicyh, sourh, sweeth, dryh, bitterh]
flav_group = ["SPICY", "SOUR", "SWEET", "DRY", "BITTER"]
flav_group2 = ["SPICY", "SOUR", "SWEET", "DRY", "BITTER"]

def swap_to_all_combos():
    global flavors
    global flav_group
    flavors = []
    flav_group = []
    flavor_set = {('Green', (20, 21, 22, 23)), ('Pink', (10, 11, 13, 14)), ('Purple', (1, 3, 4, 11, 13, 14)), ('Indigo', (10, 11, 14, 15, 16, 19)), ('Brown', (10, 11, 13, 20, 21, 23)), ('Grey', (1, 3, 11, 13, 21, 23)), ('Blue', (15, 16, 17, 19)), ('Brown', (1, 3, 4, 10, 11, 13, 14)), ('Indigo', (15, 16, 17, 20, 21, 22)), ('Grey', (1, 4, 11, 14, 16, 19)), ('Brown', (10, 11, 13, 14, 15, 16, 19)), ('Brown', (10, 11, 13, 14, 20, 21, 23)), ('Grey', (1, 2, 3, 4, 11, 14, 16, 19)), ('Indigo', (10, 11, 14, 15, 16, 17, 19)), ('Grey', (3, 4, 5, 7, 8, 9, 13, 14)), ('Brown', (5, 8, 9, 10, 11, 13, 14)), ('Purple', (1, 2, 3, 21, 22, 23)), ('Grey', (5, 7, 9, 10, 14, 15, 16, 17, 19)), ('Olive', (5, 7, 8, 9, 10, 13, 14)), ('Purple', (1, 2, 3, 4, 11, 13, 14)), ('Grey', (1, 2, 16, 17, 21, 22)), ('Indigo', (15, 16, 17, 19, 20, 21, 22)), ('Light Blue', (15, 16, 17, 20, 21, 22, 23)), ('Purple', (1, 2, 4, 16, 17, 19)), ('Light Blue', (1, 2, 3, 20, 21, 22, 23)), ('Red', (1, 2, 3, 4)), ('Grey', (1, 2, 15, 16, 17, 19, 21, 22)), ('Grey', (1, 2, 3, 4, 16, 17, 19, 21, 22)), ('Grey', (2, 4, 5, 7, 8, 9, 17, 19)), ('Brown', (5, 8, 9, 10, 13, 14)), ('Grey', (1, 2, 3, 16, 17, 20, 21, 22, 23)), ('Indigo', (5, 7, 9, 15, 16, 17, 19)), ('Olive', (5, 7, 8, 9, 15, 17, 19)), ('Grey', (1, 2, 3, 4, 11, 13, 14, 21, 23)), ('Grey', (1, 2, 3, 4, 16, 17, 21, 22)), ('Indigo', (5, 7, 9, 15, 17, 19)), ('Grey', (5, 9, 10, 14, 15, 19)), ('Indigo', (1, 2, 4, 15, 16, 17, 19)), ('Grey', (2, 4, 7, 9, 17, 19)), ('Purple', (1, 2, 3, 4, 16, 17, 19)), ('Grey', (5, 7, 15, 17, 20, 21, 22, 23)), ('Grey', (1, 2, 3, 4, 16, 17, 21, 22, 23)), ('Purple', (1, 2, 3, 4, 21, 22, 23)), ('Grey', (1, 3, 10, 11, 13, 14, 21, 23)), ('Purple', (2, 3, 4, 7, 8, 9)), ('Grey', (3, 4, 5, 8, 9, 10, 11, 13, 14)), ('Olive', (2, 3, 4, 5, 7, 8, 9)), ('Grey', (1, 2, 3, 16, 17, 21, 22, 23)), ('Grey', (1, 2, 16, 17, 20, 21, 22, 23)), ('Grey', (1, 2, 3, 4, 7, 9, 17, 19)), ('Grey', (3, 4, 8, 9, 10, 11, 13, 14)), ('Gold', (15, 16, 17, 19, 20, 21, 22)), ('Gold', (5, 7, 9, 15, 16, 17, 19)), ('Gold', (15, 16, 17, 19)), ('Grey', (2, 4, 7, 9, 15, 16, 17, 19)), ('Grey', (1, 2, 4, 11, 14, 16, 17, 19)), ('Grey', (5, 7, 8, 9, 10, 14, 15, 19)), ('Grey', (10, 11, 15, 16, 20, 21)), ('Light Blue', (10, 11, 13, 20, 21, 22, 23)), ('Grey', (10, 11, 15, 16, 17, 19, 20, 21)), ('Yellow', (5, 7, 8, 9)), ('Grey', (1, 3, 4, 11, 13, 14, 21, 23)), ('Grey', (5, 7, 15, 17, 20, 22)), ('Grey', (2, 3, 4, 7, 8, 9, 17, 19)), ('Grey', (1, 3, 11, 13, 20, 21, 22, 23)), ('Grey', (1, 3, 10, 11, 13, 14, 20, 21, 23)), ('Purple', (1, 2, 3, 4, 7, 8, 9)), ('Grey', (5, 7, 15, 16, 17, 19, 20, 22)), ('Grey', (5, 7, 15, 16, 17, 20, 21, 22, 23)), ('Grey', (2, 3, 4, 7, 8, 9, 13, 14)), ('Grey', (1, 2, 4, 16, 17, 19, 21, 22)), ('Grey', (1, 2, 15, 16, 17, 20, 21, 22, 23)), ('Grey', (1, 4, 11, 14, 15, 16, 17, 19)), ('Grey', (5, 7, 9, 10, 14, 15, 17, 19)), ('Grey', (5, 7, 8, 9, 10, 14, 15, 17, 19)), ('Gold', (10, 11, 14, 15, 16, 17, 19)), ('Grey', (1, 2, 3, 4, 11, 13, 21, 23)), ('Grey', (10, 11, 14, 15, 16, 19, 20, 21)), ('Grey', (1, 3, 4, 10, 11, 13, 14, 21, 23)), ('White', (2, 7, 17, 22)), ('Grey', (2, 3, 4, 5, 7, 8, 9, 17, 19)), ('Grey', (3, 4, 5, 8, 9, 10, 13, 14)), ('Gold', (1, 2, 3, 4, 11, 13, 14)), ('Gold', (1, 2, 3, 4, 16, 17, 19)), ('Grey', (5, 8, 9, 10, 11, 13, 14, 15, 19)), ('Gold', (1, 3, 4, 10, 11, 13, 14)), ('Gold', (5, 8, 9, 10, 11, 13, 14)), ('Grey', (5, 8, 9, 10, 13, 14, 15, 19)), ('Gold', (10, 11, 13, 14, 20, 21, 23)), ('Grey', (10, 11, 13, 14, 15, 16, 20, 21)), ('Gold', (15, 16, 17, 20, 21, 22, 23)), ('Grey', (3, 4, 5, 7, 8, 9, 10, 13, 14)), ('Gold', (5, 7, 8, 9, 15, 17, 19)), ('Gold', (1, 2, 3, 4, 21, 22, 23)), ('Grey', (1, 2, 3, 4, 11, 13, 21, 22, 23)), ('Gold', (1, 3, 4, 11, 13, 14)), ('Grey', (5, 7, 9, 15, 16, 17, 19, 20, 22)), ('Grey', (5, 7, 9, 15, 17, 19, 20, 22)), ('Grey', (5, 7, 8, 9, 10, 13, 14, 15, 19)), ('Gold', (5, 7, 8, 9, 10, 13, 14)), ('Grey', (1, 2, 3, 11, 13, 21, 22, 23)), ('Grey', (5, 9, 10, 11, 13, 14, 15, 19)), ('Olive', (5, 7, 8, 9, 20, 22, 23)), ('Grey', (1, 2, 15, 16, 17, 19, 20, 21, 22)), ('Grey', (3, 4, 8, 9, 13, 14)), ('Grey', (1, 2, 3, 4, 8, 9, 13, 14)), ('Grey', (2, 3, 7, 8, 20, 21, 22, 23)), ('Grey', (2, 3, 4, 5, 7, 8, 9, 13, 14)), ('Grey', (1, 2, 3, 4, 7, 8, 9, 13, 14)), ('Grey', (5, 9, 10, 14, 15, 16, 17, 19)), ('Grey', (1, 3, 4, 8, 9, 10, 11, 13, 14)), ('Gold', (10, 11, 13, 14)), ('Grey', (1, 3, 10, 11, 13, 20, 21, 23)), ('Grey', (2, 3, 7, 8, 22, 23)), ('Light Blue', (5, 7, 8, 20, 22, 23)), ('Light Blue', (5, 7, 8, 20, 21, 22, 23)), ('Grey', (1, 3, 4, 11, 13, 14, 16, 19)), ('Grey', (1, 2, 3, 4, 7, 8, 22, 23)), ('Grey', (1, 2, 15, 16, 17, 20, 21, 22)), ('Grey', (1, 4, 10, 11, 14, 15, 16, 19)), ('Gold', (1, 2, 3, 20, 21, 22, 23)), ('Gold', (1, 2, 3, 4)), ('Grey', (2, 3, 5, 7, 8, 9, 22, 23)), ('Grey', (1, 3, 4, 8, 9, 11, 13, 14)), ('Grey', (1, 3, 10, 11, 13, 20, 21, 22, 23)), ('Gold', (1, 2, 3, 21, 22, 23)), ('Grey', (10, 11, 15, 16, 20, 21, 22, 23)), ('Grey', (1, 2, 3, 7, 8, 21, 22, 23)), ('Gold', (20, 21, 22, 23)), ('Gold', (2, 3, 4, 5, 7, 8, 9)), ('Grey', (2, 3, 4, 7, 8, 9, 22, 23)), ('Grey', (5, 7, 8, 15, 17, 20, 22, 23)), ('Grey', (2, 3, 5, 7, 8, 20, 22, 23)), ('Grey', (5, 7, 15, 16, 17, 19, 20, 21, 22)), ('Grey', (5, 9, 10, 11, 14, 15, 16, 17, 19)), ('White', (3, 8, 13, 23)), ('Grey', (2, 3, 5, 7, 8, 20, 21, 22, 23)), ('Grey', (5, 7, 15, 16, 17, 20, 21, 22)), ('Grey', (1, 2, 3, 4, 8, 9, 11, 13, 14)), ('Gold', (5, 7, 9, 15, 17, 19)), ('Grey', (1, 2, 3, 7, 8, 20, 21, 22, 23)), ('Gold', (15, 16, 17, 20, 21, 22)), ('Grey', (5, 7, 8, 9, 15, 17, 20, 22)), ('Grey', (1, 2, 4, 15, 16, 17, 19, 21, 22)), ('Grey', (1, 2, 3, 4, 11, 14, 16, 17, 19)), ('White', (4, 9, 14, 19)), ('Grey', (1, 2, 4, 11, 14, 15, 16, 17, 19)), ('Grey', (1, 4, 10, 11, 13, 14, 16, 19)), ('Grey', (2, 4, 5, 7, 9, 15, 17, 19)), ('White', (4, 5, 7, 8, 9, 14, 19)), ('Grey', (1, 2, 3, 4, 7, 8, 9, 17, 19)), ('Grey', (5, 9, 10, 11, 13, 14, 15, 16, 19)), ('Grey', (1, 2, 3, 11, 13, 20, 21, 22, 23)), ('White', (1, 2, 3, 4, 11, 16, 21)), ('Grey', (10, 11, 14, 15, 16, 17, 19, 20, 21)), ('White', (1, 11, 15, 16, 17, 19, 21)), ('Grey', (5, 7, 8, 9, 15, 17, 19, 20, 22)), ('Grey', (5, 8, 10, 13, 20, 23)), ('Grey', (5, 7, 8, 15, 17, 20, 21, 22, 23)), ('White', (2, 7, 17, 20, 21, 22, 23)), ('White', (1, 11, 16, 21)), ('White', (1, 2, 4, 11, 16, 17, 19, 21)), ('Grey', (1, 2, 4, 7, 9, 16, 17, 19)), ('White', (2, 5, 7, 8, 9, 17, 22)), ('Grey', (5, 9, 10, 11, 14, 15, 16, 19)), ('Grey', (1, 2, 3, 4, 11, 13, 14, 16, 19)), ('Grey', (1, 4, 10, 11, 14, 15, 16, 17, 19)), ('Grey', (10, 11, 15, 16, 17, 20, 21, 22)), ('Grey', (10, 11, 13, 15, 16, 20, 21, 23)), ('White', (1, 2, 3, 4, 7, 17, 22)), ('White', (1, 2, 3, 4, 9, 14, 19)), ('Grey', (5, 8, 10, 11, 13, 14, 20, 23)), ('Grey', (5, 8, 10, 13, 20, 21, 22, 23)), ('Gold', (5, 7, 8, 20, 21, 22, 23)), ('Gold', (1, 2, 4, 15, 16, 17, 19)), ('Grey', (1, 3, 4, 10, 11, 13, 14, 16, 19)), ('Grey', (1, 4, 10, 11, 13, 14, 15, 16, 19)), ('Grey', (10, 11, 13, 14, 15, 16, 19, 20, 21)), ('White', (1, 10, 11, 13, 14, 16, 21)), ('Grey', (5, 7, 8, 9, 10, 13, 20, 23)), ('White', (3, 5, 7, 8, 9, 13, 23)), ('Grey', (2, 3, 4, 5, 7, 8, 9, 22, 23)), ('Grey', (5, 7, 8, 9, 15, 17, 20, 22, 23)), ('Grey', (2, 3, 5, 7, 8, 9, 20, 22, 23)), ('White', (4, 9, 10, 11, 13, 14, 19)), ('Grey', (2, 4, 5, 7, 9, 15, 16, 17, 19)), ('Grey', (1, 2, 4, 7, 9, 15, 16, 17, 19)), ('Grey', (10, 11, 15, 16, 17, 20, 21, 22, 23)), ('White', (3, 5, 7, 8, 9, 10, 13, 14, 23)), ('Grey', (5, 8, 9, 10, 13, 14, 20, 23)), ('Gold', (5, 8, 9, 10, 13, 14)), ('White', (3, 5, 8, 9, 10, 13, 14, 23)), ('White', (3, 5, 8, 10, 13, 20, 23)), ('Grey', (5, 8, 9, 10, 11, 13, 14, 20, 23)), ('Gold', (5, 7, 8, 9)), ('Grey', (1, 2, 3, 4, 7, 8, 21, 22, 23)), ('Gold', (1, 2, 3, 4, 7, 8, 9)), ('White', (4, 5, 8, 9, 10, 13, 14, 19)), ('Grey', (10, 11, 15, 16, 17, 19, 20, 21, 22)), ('White', (4, 5, 8, 9, 10, 11, 13, 14, 19)), ('White', (3, 5, 8, 9, 10, 11, 13, 14, 23)), ('Grey', (5, 8, 10, 11, 13, 20, 21, 23)), ('Grey', (2, 4, 5, 7, 8, 9, 15, 17, 19)), ('White', (5, 10, 15, 16, 17, 19, 20)), ('Grey', (5, 8, 10, 11, 13, 14, 20, 21, 23)), ('White', (5, 10, 11, 13, 14, 15, 20)), ('White', (5, 10, 15, 20)), ('White', (5, 10, 11, 14, 15, 16, 19, 20)), ('Grey', (10, 11, 13, 14, 15, 16, 20, 21, 23)), ('White', (4, 9, 14, 15, 16, 17, 19)), ('Grey', (5, 7, 8, 10, 13, 20, 22, 23)), ('White', (5, 10, 15, 20, 21, 22, 23)), ('White', (1, 11, 16, 20, 21, 22, 23)), ('Gold', (10, 11, 13, 14, 15, 16, 19)), ('Grey', (10, 11, 13, 15, 16, 20, 21, 22, 23)), ('Grey', (5, 8, 10, 11, 13, 20, 21, 22, 23)), ('Grey', (1, 2, 3, 4, 7, 9, 16, 17, 19)), ('White', (1, 2, 3, 4, 11, 16, 21, 22, 23)), ('Grey', (5, 7, 8, 9, 10, 13, 14, 20, 23)), ('White', (1, 2, 3, 4, 7, 17, 21, 22, 23)), ('White', (1, 2, 3, 7, 17, 21, 22, 23)), ('White', (2, 3, 7, 8, 17, 22, 23)), ('White', (1, 2, 3, 11, 16, 21, 22, 23)), ('White', (1, 2, 3, 7, 17, 20, 21, 22, 23)), ('White', (3, 8, 10, 11, 13, 14, 23)), ('White', (3, 8, 10, 11, 13, 20, 21, 23)), ('White', (3, 8, 13, 20, 21, 22, 23)), ('Grey', (5, 7, 8, 10, 13, 20, 21, 22, 23)), ('White', (5, 7, 8, 9, 10, 15, 20)), ('Gold', (10, 11, 13, 20, 21, 22, 23)), ('Grey', (5, 7, 8, 9, 10, 13, 20, 22, 23)), ('White', (4, 5, 7, 9, 14, 15, 16, 17, 19)), ('White', (5, 7, 9, 10, 15, 17, 19, 20)), ('White', (4, 5, 7, 9, 14, 15, 17, 19)), ('White', (2, 4, 7, 9, 14, 17, 19)), ('White', (5, 7, 8, 9, 10, 15, 17, 19, 20)), ('White', (4, 5, 7, 8, 9, 14, 15, 17, 19)), ('White', (2, 5, 7, 8, 17, 20, 22, 23)), ('White', (1, 2, 3, 4, 8, 13, 23)), ('Gold', (5, 7, 8, 9, 20, 22, 23)), ('Grey', (1, 2, 3, 4, 7, 8, 9, 22, 23)), ('White', (1, 3, 4, 10, 11, 13, 14, 16, 21)), ('White', (1, 4, 11, 14, 16, 19, 21)), ('White', (1, 3, 4, 8, 11, 13, 14, 23)), ('White', (1, 2, 3, 4, 8, 11, 13, 14, 23)), ('White', (1, 2, 3, 4, 11, 13, 14, 16, 21)), ('White', (2, 3, 4, 7, 8, 9, 14, 19)), ('White', (2, 7, 15, 16, 17, 19, 22)), ('White', (5, 10, 15, 16, 17, 20, 21, 22, 23)), ('White', (5, 10, 15, 16, 17, 20, 21, 22)), ('White', (5, 10, 11, 15, 16, 20, 21)), ('White', (2, 7, 15, 16, 17, 20, 21, 22)), ('White', (2, 7, 15, 16, 17, 19, 20, 21, 22)), ('White', (5, 10, 15, 16, 17, 19, 20, 21, 22)), ('White', (3, 8, 10, 11, 13, 14, 20, 21, 23)), ('White', (1, 2, 3, 8, 13, 21, 22, 23)), ('White', (3, 8, 10, 11, 13, 20, 21, 22, 23)), ('White', (3, 5, 7, 8, 9, 10, 13, 20, 23)), ('White', (2, 7, 15, 16, 17, 20, 21, 22, 23)), ('White', (1, 2, 3, 11, 16, 20, 21, 22, 23)), ('White', (5, 7, 9, 10, 15, 16, 17, 19, 20)), ('White', (1, 3, 4, 8, 10, 11, 13, 14, 23)), ('White', (4, 5, 7, 8, 9, 10, 13, 14, 19)), ('White', (1, 2, 3, 4, 11, 16, 17, 19, 21)), ('White', (1, 2, 4, 11, 15, 16, 17, 19, 21)), ('White', (3, 5, 7, 8, 9, 13, 20, 22, 23)), ('White', (1, 3, 4, 11, 13, 14, 16, 21)), ('White', (3, 5, 8, 9, 10, 13, 14, 20, 23)), ('White', (3, 5, 8, 10, 13, 20, 21, 22, 23)), ('White', (3, 5, 8, 10, 11, 13, 14, 20, 23)), ('White', (5, 10, 11, 14, 15, 16, 17, 19, 20)), ('White', (5, 10, 11, 13, 14, 15, 16, 19, 20)), ('White', (1, 2, 3, 4, 7, 8, 9, 17, 22)), ('White', (1, 2, 3, 4, 7, 8, 17, 22, 23)), ('White', (1, 2, 3, 7, 8, 17, 21, 22, 23)), ('White', (2, 3, 5, 7, 8, 9, 17, 22, 23)), ('White', (2, 3, 7, 8, 17, 20, 21, 22, 23)), ('White', (1, 2, 4, 9, 14, 15, 16, 17, 19)), ('White', (2, 4, 7, 9, 14, 15, 16, 17, 19)), ('White', (2, 4, 5, 7, 9, 14, 15, 17, 19)), ('White', (1, 2, 3, 4, 7, 9, 14, 17, 19)), ('White', (2, 4, 5, 7, 8, 9, 14, 17, 19)), ('White', (2, 5, 7, 8, 17, 20, 21, 22, 23)), ('White', (2, 5, 7, 8, 9, 17, 20, 22, 23)), ('White', (1, 4, 10, 11, 13, 14, 16, 19, 21)), ('White', (1, 4, 11, 14, 15, 16, 17, 19, 21)), ('White', (1, 2, 3, 4, 11, 14, 16, 19, 21)), ('White', (2, 3, 4, 5, 7, 8, 9, 14, 19)), ('White', (5, 10, 11, 13, 15, 20, 21, 22, 23)), ('White', (1, 2, 3, 4, 7, 8, 9, 14, 19)), ('White', (5, 10, 11, 15, 16, 20, 21, 22, 23)), ('White', (5, 10, 11, 15, 16, 17, 20, 21, 22)), ('White', (5, 10, 11, 13, 14, 15, 16, 20, 21)), ('White', (5, 10, 11, 15, 16, 17, 19, 20, 21)), ('White', (1, 10, 11, 14, 15, 16, 19, 21)), ('White', (2, 3, 4, 7, 8, 9, 17, 22)), ('White', (3, 4, 8, 9, 10, 11, 13, 14, 19)), ('White', (4, 5, 9, 10, 11, 13, 14, 15, 19)), ('White', (1, 3, 4, 9, 10, 11, 13, 14, 19)), ('White', (4, 9, 10, 11, 13, 14, 15, 16, 19)), ('White', (5, 10, 11, 13, 15, 20, 21, 23)), ('White', (1, 2, 4, 9, 14, 16, 17, 19)), ('White', (1, 11, 15, 16, 17, 20, 21, 22, 23)), ('White', (1, 3, 11, 13, 16, 21, 23)), ('White', (1, 10, 11, 13, 16, 20, 21, 23)), ('White', (3, 5, 7, 8, 13, 20, 22, 23)), ('White', (5, 7, 8, 9, 10, 13, 14, 15, 20)), ('White', (5, 7, 8, 9, 10, 15, 17, 20, 22)), ('White', (5, 7, 8, 9, 10, 15, 20, 22, 23)), ('White', (1, 2, 3, 4, 8, 13, 21, 22, 23)), ('White', (1, 2, 3, 4, 8, 9, 13, 14, 23)), ('White', (1, 2, 3, 4, 7, 8, 9, 13, 23)), ('White', (2, 5, 7, 9, 15, 16, 17, 19, 22)), ('White', (1, 2, 7, 15, 16, 17, 19, 21, 22)), ('White', (1, 2, 4, 7, 15, 16, 17, 19, 22)), ('White', (1, 4, 9, 10, 11, 13, 14, 16, 19)), ('White', (1, 10, 11, 15, 16, 20, 21)), ('White', (5, 7, 8, 9, 10, 13, 15, 20, 23)), ('White', (1, 2, 3, 4, 7, 8, 13, 22, 23)), ('White', (2, 4, 7, 9, 15, 16, 17, 19, 22)), ('White', (1, 11, 15, 16, 17, 19, 20, 21, 22)), ('White', (5, 8, 9, 10, 13, 14, 15, 20)), ('White', (2, 5, 7, 9, 15, 17, 19, 22)), ('White', (1, 3, 4, 9, 11, 13, 14, 19))}
    #flavor_set.remove(('Black', ()))
    for item in flavor_set:
        #print(item)
        flav_group.append(str(item))
        flavors.append(list(item[1]))

def find_first(lst1, lst2):
    mini = 30
    for num in lst1:
        curr = lst2.index(num)
        if curr < mini:
            mini = curr
            lowest = num
    return (lowest)

def check_variance(trials):
    lst = []
    checks = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 200]
    for i in range(0,len(flavors)):
        lst.append([])
        for j in range(0,25):
            lst[i].append(0)
    for i in range(0, trials):
        if (i/trials*100 > checks[0]):
            print(str(checks[0]) + "%")
            checks = checks[1:]
        rnd_tbl = rand_table()
        for j in range(0,len(flavors)):
            curr = find_first(flavors[j], rnd_tbl)
            var = lst[j][curr] + 1
            lst[j][curr] = var
    return(lst)

def calculate_variance(trials):
    try:
        os.remove("VARIANCE.txt")
    except:
        pass
    f = open("VARIANCE.txt", "a")
    try:
        os.remove("VARIANCE.csv")
    except:
        pass
    f2 = open("VARIANCE.csv", "a")      
    lst = check_variance(trials)
    for i in range(0, len(flavors)):
        print("**" + str(flav_group[i]) + ":**")
        f.write("**" + str(flav_group[i]) + ":**\n")
        odds = []
        for j in range(0, len(flavors[i])):
            odds.append([lst[i][flavors[i][j]]/trials * 100, [flavors[i][j]]])
            print(natures[flavors[i][j]] + " has a " + str(round(odds[j][0], 4)) + "% occurance")
            f.write(natures[flavors[i][j]] + " has a " + str(odds[j][0]) + "% occurance\n")
        neutralOdds = odds_of_neutral(odds)
        nOdds = []
        for k in range(0, 5):
            print("The odds of a " + flav_group2[k] + " Pokeblock being neutral is: " + str(round(neutralOdds[k][0])) +"%")
            print("The odds of a " + flav_group2[k] + " Pokeblock being liked is: " + str(round(neutralOdds[k][1], 4)) +"%")
            print("The odds of a " + flav_group2[k] + " Pokeblock being hated is: " + str(round(neutralOdds[k][2], 4)) +"%")
            f.write("The odds of a " + flav_group2[k] + " Pokeblock being neutral is: " + str(neutralOdds[k][0]) +"%\n")
            f.write("The odds of a " + flav_group2[k] + " Pokeblock being liked is: " + str(neutralOdds[k][1]) +"%\n")
            f.write("The odds of a " + flav_group2[k] + " Pokeblock being hated is: " + str(neutralOdds[k][2]) +"%\n\n")
            nOdds.append(neutralOdds[k][0])
            nOdds.append(neutralOdds[k][1])
            nOdds.append(neutralOdds[k][2])
        best_nOdds = max(nOdds[0], nOdds[3], nOdds[6], nOdds[9], nOdds[12])
        naturesL=[0]*24
        for m in range(0, len(odds)):
            naturesL[odds[m][1][0]] = odds[m][0]
        f2.write(flav_group[i].replace(", ","/") + ", " + str(best_nOdds) + ", " + str(nOdds)[1:-1] + ", " + str(naturesL)[1:-1] + "\n")
        
        
    print()
    print("N = " + comma_number(trials))
    f.write("N = " + comma_number(trials))
    f.close()
    f2.close()

BEST_NEUTRAL = 0

def odds_of_neutral(loOdds):
    global BEST_NEUTRAL
    result = []
    for i in range(0, len(flavors2)):
        neutral = 0
        liked = 0
        hated = 0
        for nat in range(0, len(loOdds)):
            if loOdds[nat][1][0] in flavors2[i]:
                liked += loOdds[nat][0]
            elif loOdds[nat][1][0] in flavorsh[i]:
                hated += loOdds[nat][0]
            else:
                neutral += loOdds[nat][0]
        result.append((neutral, liked, hated))
        if neutral > BEST_NEUTRAL:
            BEST_NEUTRAL = neutral
    return result
                         
def comma_number(num):
    str_num = str(num)
    result = ''
    while len(str_num) > 3:
        result = "," + str_num[-3:] + result
        str_num = str_num[:-3]
    result = str_num + result
    return result
        
if __name__ == '__main__':
    #swap_to_all_combos()
    #calculate_variance(10000000)
    #input("GET BEST")
    #print(BEST_NEUTRAL)
    #input('DONE')
    pass