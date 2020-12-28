import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

#Safari Zone Encounter Tables
east = [24, 26, 23, 25, 22, 33, 24, 25, 22, 25, 22, 28]
north = [26,30,25,27,23,30,30,32,23,26,23,28]
west = [26, 22, 25, 27, 23, 30, 30, 32, 23, 25, 23, 28]
enter = [25, 22, 24, 25, 22, 31, 31, 30, 22, 23, 22, 23]


def pp_rand_variance(mod_var, result0 = -1, result1 = -1):
    mylist = []
    for x in range(0, mod_var):
        mylist.append(0)
    for i in range(0, 65536):
        modded = i % mod_var
        mylist[modded] += 1
    if result0 == -1:
        for z in range(0, mod_var):
            print(str(z) + " has " + str(mylist[z]) + " occurences")
    else:
        res = 0
        for i in range(result0, result1 + 1):
            res += mylist[i]
        print("There are " + str(res) + " ways to roll between " + str(result0) + " & " + str(result1))
        odds = res/65_536
        print(str(odds * 100) + "%")
        return(odds)

def get_enc_slot_ow():
    slots = []
    print("SLOT 0:")
    slots.append(pp_rand_variance(100, 0, 19))
    print("")
    print("SLOT 1:")
    slots.append(pp_rand_variance(100, 20, 39))
    print("")
    print("SLOT 2:")
    slots.append(pp_rand_variance(100, 40, 49))
    print("")
    print("SLOT 3:")
    slots.append(pp_rand_variance(100, 50, 59))
    print("")
    print("SLOT 4:")
    slots.append(pp_rand_variance(100, 60, 69))
    print("")
    print("SLOT 5:")
    slots.append(pp_rand_variance(100, 70, 79))
    print("")
    print("SLOT 6:")
    slots.append(pp_rand_variance(100, 80, 84))
    print("")
    print("SLOT 7:")
    slots.append(pp_rand_variance(100, 85, 89))
    print("")
    print("SLOT 8:")
    slots.append(pp_rand_variance(100, 90, 93))
    print("")
    print("SLOT 9:")
    slots.append(pp_rand_variance(100, 94, 97))
    print("")
    print("SLOT 10:")
    slots.append(pp_rand_variance(100, 98, 98))
    print("")
    print("SLOT 11:")
    slots.append(pp_rand_variance(100, 99, 99))
    print("")
    return (slots)

def get_repel_odds(level_slots, target_slot):
    blockPrint()
    slot_odds = get_enc_slot_ow()
    total_odds = 0
    under_level_list = get_repelled_slot(level_slots, level_slots[target_slot])
    for i in range(0, 12):
        if i not in under_level_list:
            total_odds += slot_odds[i]
    target_odds = slot_odds[target_slot]/total_odds
    enablePrint()
    print("There is a " + str(100*(1-total_odds)) + "% chance of repel triggering")
    print("The odds of encountering SLOT " + str(target_slot) + " is " + str(target_odds * 100) + "%")
    return target_odds

def get_repelled_slot(level_slots, target_level):
    repelled_slots = []
    for i in range(0, 12):
        if level_slots[i] < target_level:
            repelled_slots.append(i)
    return repelled_slots