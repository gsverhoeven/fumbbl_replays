def parse_blockchoice(blockobj):

    block_symbols = ['@', '%', '>', '>', '!', '*']

    block_roll = []
    for die_index in range(abs(blockobj['nrOfDice'])): # nrOfDice can be negative: opp chooses
        block_roll.append(block_symbols[blockobj['blockRoll'][die_index] - 1])

    die_chosen = blockobj['diceIndex']

    out_string = "Block roll:" + str(block_roll) + " | block result: " + \
        str(block_symbols[blockobj['blockRoll'][die_chosen] - 1]) + " (" + blockobj['blockResult'] + ")"

    return out_string