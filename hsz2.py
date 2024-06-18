import random
import HSZC
import pprand

natures = ['Hard', 'Lonely', 'Brave', 'Adamant', 'Naughty', 'Bold', 'Docile', 'Relaxed', 'Impish', 'Lax', 'Timid', 'Hasty', 'Serious', 'Jolly', 'Naive', 'Modest', 'Mild', 'Quiet', 'Bashful', 'Rash', 'Calm', 'Gentle', 'Sassy', 'Careful', 'Quirky']


odds_of_trigger = pprand.pp_rand_variance(100, 0, 79)
odds_of_flee = pprand.pp_rand_variance(100, 0, 14)
pprand.enablePrint()

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
    pprand.enablePrint()
    if current_flav == -1:
        odds_of_trigger = 0

    rand_odds_of_flav_yum = 4/25 * (1 - odds_of_trigger)
    rand_odds_of_flav_yuck = 4/25 * (1 - odds_of_trigger)
    rand_odds_of_flav_fine = (25 - 8)/25 * (1 - odds_of_trigger)
    # 0 SPICY, 1 SOUR, 2 SWEET, 3 DRY, 4 BITTER
    if current_flav >= 0 and current_flav != throw_flav:
        trigger_odds_of_flav_yuck = odds_of_trigger * (trigger_flavs[current_flav][throw_flav])
        trigger_odds_of_flav_fine = odds_of_trigger * (1 - trigger_flavs[current_flav][throw_flav])
        #trigger_odds_of_flav_yuck = odds_of_trigger * (0)
        #trigger_odds_of_flav_fine = odds_of_trigger * (1)        
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
    global odds_of_flee
    # GET ODDS OF FAILING ROLL 1 (IGNORED)
    fail_odds = get_odds_of_rate(3, current_flav, throw_flav) * (1 - odds_of_flee)    
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
    odds_of_flee = 1 - pprand.pp_rand_variance(100, 0, 14)
    pprand.enablePrint()    
    if current_flav == "SYNC_ONLY":
        odds_of_0 = (0.5 + 0.5 * (25 - 8)/25) * odds_of_flee
        odds_of_1 = (0.5 * (1-((25 - 4)/25))) * odds_of_flee
        odds_of_3 = (0.5 * (1-((25 - 4)/25))) * odds_of_flee
        if extra_throw == 1:
            odds_of_0 += (0.5 * (1-((25 - 4)/25))) * odds_of_flee * 1/4 * odds_of_flee
            odds_of_1 += (0.5 * (1-((25 - 4)/25))) * odds_of_flee * 3/4 * odds_of_flee
            odds_of_3 = 0
    elif current_flav == "COMPLEX":
        # 0 = NEUTRAL, 1 = LIKED 3 = DISLIKED
        odds_of_0 = (odds_of_trigger + (1-odds_of_trigger) * (25 - 8)/25) * odds_of_flee
        odds_of_1 = ((1-odds_of_trigger) * (1-((25 - 4)/25))) * odds_of_flee
        odds_of_3 = ((1-odds_of_trigger) * (1-((25 - 4)/25))) * odds_of_flee
        if extra_throw == 1:
            odds_of_0 += ((1-odds_of_trigger) * (1-((25 - 4)/25))) * odds_of_flee * 1/4 * odds_of_flee
            odds_of_1 += ((1-odds_of_trigger) * (1-((25 - 4)/25))) * odds_of_flee * 3/4 * odds_of_flee
            odds_of_3 = 0        
    elif current_flav == "SYNC_COMPLEX":
        odds_of_0 = (odds_of_trigger + (1-odds_of_trigger) * 0.5 + (1-odds_of_trigger) * 0.5 * (25 - 8)/25) * 0.85
        odds_of_1 = ((1-odds_of_trigger) * 0.5 * (1-((25 - 4)/25))) * odds_of_flee
        odds_of_3 = ((1-odds_of_trigger) * 0.5 * (1-((25 - 4)/25))) * odds_of_flee
        if extra_throw == 1:
            odds_of_0 += ((1-odds_of_trigger) * 0.5 * (1-((25 - 4)/25))) * odds_of_flee * 1/4 * odds_of_flee
            odds_of_1 += ((1-odds_of_trigger) * 0.5 * (1-((25 - 4)/25))) * odds_of_flee * 3/4 * odds_of_flee
            odds_of_3 = 0          
    else:
        odds_of_0 = get_odds_of_rate(0, current_flav, throw_flav) * odds_of_flee
        odds_of_1 = get_odds_of_rate(1, current_flav, throw_flav) * odds_of_flee
        odds_of_3 = get_odds_of_rate(3, current_flav, throw_flav) * odds_of_flee
    s0 = HSZC.pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, cr, 0)[0]
    s1 = HSZC.pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, cr, 1)[0]
    s3 = HSZC.pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, cr, 3)[0]
    odds_of_success_0 = s0 * odds_of_0
    odds_of_success_1 = s1 * odds_of_1
    odds_of_success_3 = s3 * odds_of_3
    if extra_throw == 1 and current_flav not in ("SYNC_ONLY", "COMPLEX", "SYNC_COMPLEX"):
        odds_of_success_3 = get_odds_yum_2(current_flav, throw_flav)[0] * odds_of_flee *  s0 + get_odds_yum_2(current_flav, throw_flav)[1] * odds_of_flee * s1
    return odds_of_success_0 + odds_of_success_1 + odds_of_success_3
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
flavors = [spicy, sour, sweet, dry, bitter]
flav_group = ["SPICY", "SOUR", "SWEET", "DRY", "BITTER"]

def find_first(lst1, lst2):
    mini = 30
    for num in lst1:
        curr = lst2.index(num)
        if curr < mini:
            mini = curr
            lowest = num
    return (lowest)

def check_variance(trials):
    try:
        os.remove("VARIANCE.txt")
    except:
        pass
    f = open("VARIANCE.txt", "a")    
    lst = []
    checks = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 200]
    for i in range(0,25):
        lst.append(0)
    for i in range(0, trials):
        if (i/trials*100 > checks[0]):
            print(str(checks[0]) + "%")
            checks = checks[1:]
        rnd_tbl = rand_table()
        print(rnd_tbl)
        for flav in flavors:
            curr = find_first(flav, rnd_tbl)
            var = lst[curr] + 1
            lst[curr] = var
    return(lst)

def calculate_variance(trials):
    lst = check_variance(trials)
    for i in range(0, len(flavors)):
        print("**" + flav_group[i] + ":**")
        for j in range(0, len(flavors[i])):
            odds = lst[flavors[i][j]]/trials * 100
            print(natures[flavors[i][j]] + " has a " + str(odds) + "% occurance")
    print()
    print("N = " + comma_number(trials))
          
def comma_number(num):
    str_num = str(num)
    result = ''
    while len(str_num) > 3:
        result = "," + str_num[-3:] + result
        str_num = str_num[:-3]
    result = str_num + result
    return result
        
if __name__ == '__main__':
    #print(calculate_variance(10000))
    #input('DONE')
    pass