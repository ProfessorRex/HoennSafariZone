import math
import concurrent.futures
import time
import hsz2

'''
PLEASE DON'T JUDGE LAZY CODE
this is just for fun <3
'''



def calculate_catch_rate(rate, rock=False, bait=False):
    '''Can only accept EITHER balls OR Rocks
    The FRLG games use a fairly odd catch formula
    the catch rate of a pokemon is modified to a 'catch factor' and then
    back to a catch rate by multiplying it by 100/1275, modifiying for 
    any bait or balls that have been thrown, then multiplying by 1275/100
    again. Since division doesn't maintain floating point numbers in this case
    most catch rates are modified and end up being lower
    SEE NOTE AT END FOR ALL THE RATES BEFOER AND AFTER MODIFICATION
    '''
    # pull the modified catch rate
    rate = get_catch_factor(rate, rock, bait)[0]
    # calculate catch rate after ball and health (full health with a safari ball)
    a = int(int((rate * 15) /10)/3)
    if a >= 255:
        p = 1    
    else:
        # odds of a shake
        b = int(int('0xffff0', 16)/(int(math.sqrt(int(
                 math.sqrt(int('0xff0000', 16)/a))))))
        # odds of successful capture
        p = pow((b/65536), 4)
    return p


def get_catch_factor(rate, rock=False, bait=False):
    '''
    The game multiplies the Pokemon's base catch rate by 100/1275
    to get a 'Catch Factor'
    the catch factor is modified by bait or balls however the devs
    put in a minimum of '3' after bait which actually increases Chansey's
    catch factor from 2 -> 3
    there is also a maximum of 20
    THESE MODIFIERS ARE PERMANENT AND ARE NOT REMOVED EVEN IF THE POKEMON STOPS
    EATING OR BEING ANGRY
    '''
    factor = int(int((rate * 100)/255)/5)
    if rock > 0:
        # Bait and balls stack
        factor = int(rate * 2 * rock)
    elif bait > 0:
        factor = int(factor * 0.5 * bait)
    # Iff bait or rocks have been used the game has max & min values
    if (bait or rock) and (factor < 3):
        # Minimum is 3 effectivley 38 Catch rate
        factor = 3
    if (bait or rock) and (factor > 20):
        # Max is 20 which is a 255 catch rate
        factor = 20
    rate = int(factor * 1275/100)
    return (rate, factor)


def calculate_flee_rate(rate, angry, eating):
    # Get the 'flee factor'
    rate = rate
    # When the rate is pulled from game files
    # there is a minimum of 2
    #if rate < 2:
        #rate = 2    
    # OTHER STUFF TO DO - ROCKS
    if eating:
        # Divide flee rate by 4 if eating
        # based off a floored version of the flee factor / 4
        rate = int(rate/4)
    #if rate < 1:
        # there is a bare minimum flee rate so bait cannot drop it below
        # 5% per turn
        #rate = 1
    # The game generates a random # and compares it to 5 x the flee rate
    # Get the odds of fleeing per turn (%)
    flee_odds = rate * 5
    # Due to non-even distribution of random number generation
    # We need to adjust this slightly
    if flee_odds > 36:
        sub = flee_odds - 36
        p = ((flee_odds * 656) - sub)/65_536
    else:
        p = (flee_odds * 656)/65_536
    return p


def balls_only_catch(catch_rate, flee_rate):
    '''
    USED TO GET THE ODDS OF CAPTURE WITHOUT ANY BAIT
    INT catch_rate - the pokemons base catch rate
    INT flee_rate - base flee rate
    '''
    # get the odds of capture per ball
    p_catch = calculate_catch_rate(catch_rate, 0, 0)
    # get odds of fleeing per ball
    p_flee = calculate_flee_rate(flee_rate, False, False)
    # Run the first turn
    round_vals = odds_of_catch(1, p_catch, p_flee)
    p_success = round_vals[1]
    p_failure = round_vals[2]
    balls = 1
    #Throw balls until we run out
    while balls < 30:
        round_vals = odds_of_catch(round_vals[0], p_catch, p_flee)
        p_success += round_vals[1]
        p_failure += round_vals[2]
        balls += 1
    p_failure += round_vals[0]
    #Return the probability of successfully catching the Chansey vs not
    return (p_success, p_failure)

def odds_of_catch(p_turn, p_catch, p_flee):
    '''FOR ODDS BY TURN - TAKES INTO ACCOUNT ODDS OF GETTING TO SAID TURN'''
    # The probability to catch on any ball throw is:
    # the odds of getting to the turn x the odds of catching with one ball
    p_catch_new = p_catch * p_turn
    # The odds of flee after any ball throw is:
    # the odds of getting to the turn x the odds of not catching * odds of flee
    p_flee = (1 - p_catch) * p_turn * p_flee
    # the odds to get to the next turn is just whatever is left over
    p_continue = p_turn - p_catch_new - p_flee
    return (p_continue, p_catch_new, p_flee)

def add_bait(bait_to_add, current_bait):
    '''
    Takes in the currently remaining amount of bait in a pile
    adds the amount of bait rolled from the bait throw's RNG
    NOTE: Bait seems to be equally distributed between 2-6 turns
    Bait maxes at 6
    think of bait as being a pile though, each throw adds to the pile
    and does NOT reset the pile
    '''
    if (current_bait <= 0):
        current_bait = bait_to_add
    else:
        current_bait = current_bait + bait_to_add
    # set bait to the max of 6
    if current_bait > 6:
        current_bait = 6
    return current_bait

def pattern_odds_catch(turns='L',  r=0, catch_rate=30, flee_rate=125):
    '''
    catch_rate -> INT (Base catch rate of pokemon)
    flee_rate -> INT (Base flee rate of the pokemon)
    turns -> String ('R' Rock, 'T' Bait. 'L' Ball) ex 'TLTLLLTLL'
    r -> INT (0 = no repeat, hard run pattern), (1 = repeat pattern if bait ends), (2 = if bait fails, move to balls)
    amount_of_bait -> int 0 to 6 (Amount of bait left at the start of the turn)
    baited -> default is false but should be true if any bait has been thrown
    t -> retention of the overall pattern in recursive calls
    RETURN
    p_success -> probability of catching the pokemon using the pattern of turns
    p_failure -> probability of failing the capture
    '''    
    # Get catch rates and flee rates
    p_flee_watching = calculate_flee_rate(flee_rate, False, False)
    p_flee_eating = calculate_flee_rate(flee_rate, False, True)
    p_catch = calculate_catch_rate(catch_rate, 0, 1)
    p_catch_unbaited = calculate_catch_rate(catch_rate, 0, 0)    
    result = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch, p_catch_unbaited, turns, r)
    return (result[0], result[1], turns)

def pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns, r, p_turn=1, amount_of_bait=0, baited=False, t=0):
    '''
    catch_rate -> INT (Base catch rate of pokemon)
    flee_rate -> INT (Base flee rate of the pokemon)
    p_turn -> float <= 1 (the odds of the current turn occuring)
    turns -> String ('R' Rock, 'T' Bait. 'L' Ball) ex 'TLTLLLTLL'
    r -> BOOL true for restarting patterns, False to not
    amount_of_bait -> int 0 to 6 (Amount of bait left at the start of the turn)
    baited -> default is false but should be true if any bait has been thrown
    t -> retention of the overall pattern in recursive calls
    RETURN
    p_success -> probability of catching the pokemon using the pattern of turns
    p_failure -> probability of failing the capture
    '''
    #If this is the first turn store the full pattern
    #is reduced by one function after each turn
    if t == 0:
        t = turns
    if len(turns) > 0:
        turn = turns[0]
    else:
        p_success = 0
        p_failure = p_turn
        return (p_success, p_failure)
    p_success = 0
    p_failure = 0
    # Cycle through the pattern of turns until there are no turns left
    # OPTIMIALLY THE PATTERN WILL UTILIZE ALL 30 BALLS
    # DETERMINE IF THE POKEMON IS EATING
    p_catch = p_catch_baited
    if amount_of_bait > 0:
        eating = True
        p_flee = p_flee_eating
        baited = True
        #Amount of bait is reduced later (at end of round, before next check)
    else:
        eating = False
        p_flee = p_flee_watching
        if not baited:
            p_catch = p_catch_unbaited
    # If a ball was thrown get the odds of capture vs fleet
    if turn == 'L' and (eating or r == 0):
        round_vals = odds_of_catch(p_turn, p_catch, p_flee)
        ##print(round_vals[1])
        p_success = p_success + round_vals[1]
        p_failure = p_failure + round_vals[2]
        p_turn = round_vals[0]
        #MOVE TO NEXT TURN
        if(amount_of_bait > 0):
            amount_of_bait -= 1
        round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns[1:], r, p_turn, amount_of_bait, baited, t[:-1])
        p_success = p_success + round_vals[0]
        p_failure = p_failure + round_vals[1]
    # If bait is to be thrown run the probabilities for each amount of bait
    elif turn == 'T' and (eating or (not baited) or r == 0):
        # add probability of fleeing on current turn
        p_failure = p_failure + (p_turn * p_flee)
        if amount_of_bait <= 0:
            for i in (2, 3, 4, 5, 6):
                #includes bait reduction for end-of-round
                new_bait = i - 1
                # Get the probability of adding the current amount of bait
                # Multiplied by the odds of not fleeing
                if i == 2:
                    p_add_curr_bait = p_turn * 13108/65536 * (1 - p_flee)
                else:
                    p_add_curr_bait = p_turn * 13107/65536 * (1 - p_flee)
                round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns[1:], r, p_add_curr_bait, new_bait, True, t)
                p_success = p_success + round_vals[0]
                p_failure = p_failure + round_vals[1]
        elif amount_of_bait == 1:
            for i in (2, 3, 4, 5):
                #includes bait reduction for end-of-round
                new_bait = i
                # Get the probability of adding the current amount of bait
                # Multiplied by the odds of not fleeing
                if i == 2:
                    p_add_curr_bait = p_turn * 13108/65536 * (1 - p_flee)                
                elif i != 5:
                    p_add_curr_bait = p_turn * 13107/65536 * (1 - p_flee)
                else:
                    p_add_curr_bait = p_turn * 26214/65536 * (1 - p_flee)
                round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns[1:], r, p_add_curr_bait, new_bait, True, t)
                p_success = p_success + round_vals[0]
                p_failure = p_failure + round_vals[1]
                # print('Still working')
        elif amount_of_bait == 2:
            for i in (2, 3, 4):
                #includes bait reduction for end-of-round
                new_bait = i + 1
                # Get the probability of adding the current amount of bait
                if i == 2:
                    p_add_curr_bait = p_turn * 13108/65536 * (1 - p_flee)  
                elif i != 4:
                    p_add_curr_bait = p_turn * 13107/65536 * (1 - p_flee)
                else:
                    p_add_curr_bait = p_turn * 39321/65536 * (1 - p_flee)
                round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns[1:], r, p_add_curr_bait, new_bait, True, t)
                p_success = p_success + round_vals[0]
                p_failure = p_failure + round_vals[1]
        elif amount_of_bait == 3:
            for i in (2, 3):
                #includes bait reduction for end-of-round
                new_bait = i + 2
                # Get the probability of adding the current amount of bait
                if i != 3:
                    p_add_curr_bait = p_turn * 13108/65536 * (1 - p_flee)
                else:
                    p_add_curr_bait = p_turn * 52428/65536 * (1 - p_flee)
                round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns[1:], r, p_add_curr_bait, new_bait, True, t)
                p_success = p_success + round_vals[0]
                p_failure = p_failure + round_vals[1]
        else:
            #includes bait reduction for end-of-round
            new_bait = 5
            # Get the probability of adding the current amount of bait
            p_add_curr_bait = p_turn * (1 - p_flee)
            round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, turns[1:], r, p_add_curr_bait, new_bait, True, t)
            p_success = p_success + round_vals[0]
            p_failure = p_failure + round_vals[1]
    elif (r == 1):
        # IF A BALL, AND r = repeat, BUT THE POKEMON IS NOT EATING START THE PATTERN AGAIN
        # IF A BALL, BUT THE POKEMON IS NOT EATING START THE PATTERN AGAIN
        # Start the pattern again with the same number of still remaining balls
        #Get new number of turn
        n_balls = turns.count('L')
        new_turns = ''
        balls = 0
        i = 0
        while balls < n_balls:
            new_turns = new_turns + t[i]
            if t[i] == 'L':
                balls +=1
            i += 1
        round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, new_turns, r, p_turn, 0, baited, t)
        p_success = round_vals[0]
        p_failure = round_vals[1]
    elif (r == 2):
        #IF A BALL AND THE POKEMON IS NOT eating but r = balls after fail
        #remake pattern as Balls and change to no-repeat
        n_balls = turns.count('L')
        new_turns = 'L' * n_balls
        r = 0
        round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, new_turns, r, p_turn, 0, baited, t)
        p_success = round_vals[0]
        p_failure = round_vals[1]
    elif (r == 3):
        #IF a ball and the pokemon is NOT run with optimal pattern odds
        n_balls = turns.count('L')
        new_turns = get_best_pattern(n_balls, t, p_flee_watching)
        if (new_turns[1] < 1):
            p_success = new_turns[1] * p_turn
            p_failure = new_turns[2] * p_turn
        else:
            round_vals = pattern_odds_catch_deep(p_flee_watching, p_flee_eating, p_catch_baited, p_catch_unbaited, new_turns[0], r, p_turn, 0, baited, t)
            p_success = round_vals[0]
            p_failure = round_vals[1]
    return (p_success, p_failure)



def pretty_outputs(catch_rate=30, flee_rate=125, name='CHANSEY'):
    print()
    print()
    print()
    print()
    print("**OUTPUT FOR " + name + "**")
    print("Base catch rate: " + str(catch_rate))
    factor = get_catch_factor(catch_rate, 0, 0)
    print("Base catch factor: " + str(factor[1]))
    print("Modified catch rate: " + str(factor[0]))
    p_catch = calculate_catch_rate(catch_rate, 0, 0)
    print("Odds of capture per ball: " + str(round((p_catch * 100), 2)) + "%")
    fleet_ub = calculate_flee_rate(flee_rate, False, False)
    print("Odds of fleeing per turn: " +
          str(round((fleet_ub * 100), 2)) + "%")
    odds_b = pattern_odds_catch('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL', 0, catch_rate, flee_rate)
    print("Odds of capture with balls only: " +
          str(round((odds_b[0] * 100), 2)) + "%")
    print()
    print("Odds of capture with random nature: " +
          str(round((hsz2.get_catch_odds(catch_rate, -1, 1, 1) * 100), 3)) + "%")
    print("Odds of capture with Synchronizer: " +
          str(round((hsz2.get_catch_odds(catch_rate, "SYNC_ONLY", 0, 1) * 100), 2)) + "%")     
    print("Odds of capture with spicy table: " +
          str(round((hsz2.get_catch_odds(catch_rate, 0, 1, 1) * 100), 2)) + "%")
    print("Odds of capture with sour table: " +
          str(round((hsz2.get_catch_odds(catch_rate, 1, 0, 1) * 100), 2)) + "%")
    print("Odds of capture with sweet table: " +
          str(round((hsz2.get_catch_odds(catch_rate, 2, 0, 1) * 100), 2)) + "%")
    print("Odds of capture with dry table: " +
          str(round((hsz2.get_catch_odds(catch_rate, 3, 0, 1) * 100), 2)) + "%")
    print("Odds of capture with bitter table: " +
          str(round((hsz2.get_catch_odds(catch_rate, 4, 0, 1) * 100), 2)) + "%")   
    print("Odds of capture with Complex Block: " +
          str(round((hsz2.get_catch_odds(catch_rate, "COMPLEX", 0, 1) * 100), 2)) + "%")
    print("Odds of capture with Complex Block & Synchronize: " +
          str(round((hsz2.get_catch_odds(catch_rate, "SYNC_COMPLEX", 0, 1) * 100), 2)) + "%")
    print()



def all_pretty():
    pretty_outputs(45, 3, 'DODRIO, PINSIR, AIPOM, WOBBUFFET, HERACROSS, STANTLER, & MILTANK')
    pretty_outputs(60, 3, 'SEAKING, GIRAFARIG, & GLIGAR')
    pretty_outputs(75, 3, 'GOLDUCK, XATU, & OCTILLERY')
    pretty_outputs(90, 3, 'QUAGSIRE')
    pretty_outputs(120, 3, 'GLOOM, RHYHORN, TEDDIURSA, HOUNDOUR, & PHANPY')
    pretty_outputs(190, 3, 'PIKACHU, PYSDUCK, DODUO, NATU, MARILL, PINECO, SNUBBULL, SHUCKLE, & REMORAID')
    pretty_outputs(235, 3, 'MAREEP & SUNKERN')
    pretty_outputs(255, 3, 'ODDISH, GEODUDE, GOLDEEN, MAGIKARP, HOOTHOOT, LEDYBA, SPINARAK, & WOOPER')


def make_pattern(number, balls, pattern=''):
    balls = balls - pattern.count('L')
    binary = str(bin(number))[2:]
    if (len(binary) < balls):
        binary = '0' * (balls - len(binary)) + binary
    for i in range (1, balls + 1):
        if (binary[-i] == '1'):
            pattern += 'TL'
        else:
            pattern += 'L'
    return pattern

def new_pats(t_balls, start_p='T'):
    balls = t_balls - start_p.count('L')
    pats = []
    for x in range(0, balls-2):
        num = balls - x
        max_tll = int(num/2)
        min_tllll = int(num/4)
        if min_tllll == 0:
            min_tllll = 1
        for t in range(min_tllll, max_tll + 1):
            s = '2' * (t)
            max_range = int(s, base=3)
            for i in range(0, max_range + 1):
                pat = start_p
                tern = ternary(i)
                bin_p = str(tern)
                if len(bin_p) < t:
                    bin_p = '0' * (t - len(bin_p)) + bin_p
                p_sum = 0
                for p in bin_p:
                    if p == '0':
                        p_sum += 2
                        pat = pat + 'TLL'
                    elif p == '1':
                        p_sum += 3
                        pat = pat + 'TLLL'
                    elif p == '2':
                        p_sum += 4
                        pat = pat + 'TLLLL'
                p_sum += x
                if p_sum == balls:
                    pat = pat + 'L' * x
                    pats.append(pat)
    pats = list(dict.fromkeys(pats))
    return pats

def new_best(balls, pattern='', r=3, catch_rate=45, flee_rate=125):
    best_odds = 0
    pats = new_pats(balls, pattern)
    while (len(pats) % 8) != 0:
        pats.append('L')
    with concurrent.futures.ProcessPoolExecutor() as executor:
        i = 0
        while i < len(pats):
            futures = []
            for x in range (0,8):
                curr_pattern = pats[i + x]
                future = executor.submit(pattern_odds_catch, curr_pattern, r, catch_rate, flee_rate)
                futures.append(future)
            for f in concurrent.futures.as_completed(futures):
                odds = f.result()
                if odds[0] > best_odds:
                    best_pattern = odds[2]
                    best_odds = odds[0]
                    best_fail = odds[1]
                    best_i = x
            i += 8
    result = (best_i, best_pattern, best_odds, best_fail)
    print(result)

def best_patterns(balls, pattern='', r=3, catch_rate=45, flee_rate=125):
    def_balls = pattern.count('L')
    best_odds = 0
    # -1 because TL at the end is a useless simulation
    # -2 cuz it never picks TLL either
    x = '0b' + '1' * (balls - def_balls - 2)
    max_range = int(x, base=2)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        i = 0
        while i < max_range:
            futures = []
            for x in range (0,8):
                curr_pattern = make_pattern(i+x, balls, pattern)
                future = executor.submit(pattern_odds_catch, curr_pattern, r, catch_rate, flee_rate)
                futures.append(future)
            for f in concurrent.futures.as_completed(futures):
                odds = f.result()
                if odds[0] > best_odds:
                    best_pattern = odds[2]
                    best_odds = odds[0]
                    best_fail = odds[1]
                    best_i = i
            i+=8
    result = (best_i, best_pattern, best_odds, best_fail)
    print(result)


def balls_only(cr, fr):
    for i in range(1, 31):
        pattern = 'L' * i
        print(i)
        print(pattern)
        print(pattern_odds_catch(pattern, 0, cr, fr))
    pass

def all_best(cr, fr, first):
    start = time.perf_counter()
    for i in range(first, 31):
        print(i)
        new_best(i, 'T', 3, cr, fr)
        fin = time.perf_counter()
        print(f'Finished in {round(fin-start, 2)} second(s)')
    input("DONE LMAO IMPRESSIVE")

def ternary (n):
    if n == 0:
        return '0'
    nums = []
    while n:
        n, r = divmod(n, 3)
        nums.append(str(r))
    return ''.join(reversed(nums))

if __name__ == '__main__':
    print("GENERATION 3 SAFARI ZONE CALCULATOR")
    #input("PRESS ENTER TO BEGIN")
    print("Para-Venoking VERIFICATION")
    #  input("Enter the name of the Pokemon you are inquiring about")
    #balls_only(45, 75)
    #all_best(45, 75, 5)
    #make_best_patterns()
    #input('FINI')
    
