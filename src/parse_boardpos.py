def parse_boardpos(dfrow):
    boardpos = str(dfrow['CoordinateY']) + str(dfrow['PlayerCoordinateX'] + 1)
    return boardpos