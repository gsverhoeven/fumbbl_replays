import string

def parse_kickoff_scatter(obj):
    # d8 scatter direction
    # 1,2,3,4,5,6,7,8
    # N, NE, E, SE, S, SW, W, NW

    
    pos = string.ascii_lowercase[obj['ballCoordinateEnd'][1]]
    pos2 = str(obj['ballCoordinateEnd'][0] + 1)

    # long axis of the board, increasing Y coordinate (1-26) is W-E
    out_string = "Ball starts at [" + pos + pos2 + "] " + \
    "and scatters " + str(obj['rollScatterDistance']) + " squares in direction " + \
    obj['scatterDirection']

    return out_string