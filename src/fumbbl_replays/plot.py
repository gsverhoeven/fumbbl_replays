import os
import string

import importlib.resources as resources
from fumbbl_replays import __name__ as pkg_name

from PIL import Image, ImageDraw, ImageFont

from urllib.request import urlopen
from .get_cache_dir import get_cache_dir

def add_tacklezones(pitch, positions, red_team, flip = False, horizontal = False):
    for i in range(len(positions)):
        if horizontal == False:
            x = 14 - positions.iloc[i]['PlayerCoordinateY']
            y = positions.iloc[i]['PlayerCoordinateX']
        else:
            x = positions.iloc[i]['PlayerCoordinateX']
            y = positions.iloc[i]['PlayerCoordinateY']
        
        if flip == True:
            y = 25 - y
        else:
            y = y
            
        team = positions.iloc[i]['home_away']
        icon_w, icon_h = (28, 28)
        if team == red_team: # red
            tacklezone_color = (255, 0, 0) # RGB
        else:
            tacklezone_color = (0, 0, 255) # blue
        box = (icon_w * x - 28, icon_h * y - 28, icon_w * x + 2*28, icon_h * y + 2*28)
        mask = Image.new("L", (3*28, 3*28), 0).convert("RGBA")
        mask.putalpha(50)
        pitch.paste(tacklezone_color, box, mask)
    return pitch

def add_players(pitch, positions, red_team, flip = False, horizontal = False):
    square_h = 28
    square_w = 28

    if horizontal == False:
        # sort the players for drawing the lowest row on the board first (icons slightly overlap)
        # horizontal board, X from left to right is correct plotting order if we rotate CCW afterwards
        if flip == False:
            positions = positions.sort_values(by = 'PlayerCoordinateX', \
                                      ascending = True)
        else:
            positions = positions.sort_values(by = 'PlayerCoordinateX', \
                                      ascending = False)
    else:
        if flip == False:
            positions = positions.sort_values(by = 'PlayerCoordinateY', \
                                      ascending = True)
        else:
            positions = positions.sort_values(by = 'PlayerCoordinateY', \
                                      ascending = False)        

    for i in range(len(positions)):
        if horizontal == False:
            x = 14 - positions.iloc[i]['PlayerCoordinateY']
            y = positions.iloc[i]['PlayerCoordinateX']
        else:
            x = positions.iloc[i]['PlayerCoordinateX']
            y = positions.iloc[i]['PlayerCoordinateY']
        
        if flip == True:
            y = 25 - y
        else:
            y = y        
            
        team = positions.iloc[i]['home_away']
        icon_path = positions.iloc[i]['icon_path']

        icon = Image.open(urlopen(icon_path)).convert("RGBA")
        icon_w, icon_h = icon.size # still full size i.e. grid with 4 icons

        if team == red_team:
            # select first icon
            icon = icon.crop((0,0,icon_w/4,icon_w/4))
        else:
            # select third icon
            icon = icon.crop((icon_w/2, 0, icon_w*3/4, icon_w/4))

        icon_w, icon_h = icon.size # here cropped size. bigger for big guys
        shift_w = icon_w - square_w
        shift_h = icon_h - square_h
        pitch.paste(im = icon, box = (square_w * x - int(shift_w/2), \
                                      square_h * y - shift_h), \
                                        mask = icon)
        if positions.iloc[i]['PlayerState'] in ['Prone', 'Stunned']:
            draw = ImageDraw.Draw(pitch)
            draw.line((square_w * x + 2, (square_w * y) + 2, (square_h * x) + 25, (square_h * y) + 25), fill="white", width = 2)
        if positions.iloc[i]['PlayerState'] in ['Stunned']:
            draw.line((square_w * x + 25, (square_w * y) + 2, (square_h * x) + 2, (square_h * y) + 25), fill="white", width = 2)
    return pitch

def add_skill_bands(pitch, positions, flip = False, horizontal = True):
    for i in range(len(positions)):
        if horizontal == False:
            x = 14 - positions.iloc[i]['PlayerCoordinateY']
            y = positions.iloc[i]['PlayerCoordinateX']
        else:
            x = positions.iloc[i]['PlayerCoordinateX']
            y = positions.iloc[i]['PlayerCoordinateY']
        
        if flip == True:
            y = 25 - y
        else:
            y = y
            
        icon_w, icon_h = (28, 28)
        skill_colors = positions.iloc[i]['skill_colors']
        # support skill stacking, loop over list, change y pos 28 - s_nr * 3
        for s in range(len(skill_colors)):
            if skill_colors[s] != 'none':
                box = (icon_w * x, icon_h * y + (28 - (s+1) * 3), icon_w * x + 28, icon_h * y + (28 - (s * 3)))
                mask = Image.new("L", (28, 3), 0).convert("RGBA")
                pitch.paste(skill_colors[s], box, mask)  
    return pitch

def add_ball(pitch, positions, flip = False, horizontal = True, ballpos = None):
    square_h = square_w = 28
    if ballpos is None:
        # check if a player has it
        for i in range(len(positions)):
            if positions.iloc[i]['PlayerState'] == 'HasBall':
                if horizontal == False:
                    x = 14 - positions.iloc[i]['PlayerCoordinateY']
                    y = positions.iloc[i]['PlayerCoordinateX']
                else:
                    x = positions.iloc[i]['PlayerCoordinateX']
                    y = positions.iloc[i]['PlayerCoordinateY']
                
                if flip == True:
                    y = 25 - y
                else:
                    y = y
                file_path = resources.files(pkg_name) / "resources" / "sball_30x30.png"    
                icon = Image.open(file_path).convert("RGBA")
                icon = icon.resize((15, 15))
                icon_w, icon_h = icon.size
                shift_w = icon_w - square_w
                shift_h = icon_h - square_h
                pitch.paste(im = icon, box = (square_w * x - int(shift_w/2), \
                                            square_h * y - shift_h), \
                                                mask = icon)
    else:
        # ball is in a free square
        coord_y = ballpos[0] # letter
        coord_x = int(ballpos[1:]) # nr
        if horizontal == False:
            x = 14 - string.ascii_lowercase.index(coord_y)
            y = coord_x  - 1
        else:
            x = coord_x - 1
            y = string.ascii_lowercase.index(coord_y)
        
        if flip == True:
            y = 25 - y
        else:
            y = y
        file_path = resources.files(pkg_name) / "resources" / "sball_30x30.png"
        icon = Image.open(file_path).convert("RGBA")
        #icon = icon.resize((15, 15))
        icon_w, icon_h = icon.size
        shift_w = icon_w - square_w
        shift_h = icon_h - square_h
        pitch.paste(im = icon, box = (square_w * x - int(shift_w/2), \
                                    square_h * y - shift_h), \
                                        mask = icon)
    return pitch

def pitch_select_lower_half(pitch):
    pitch = pitch.crop((0, 12*28, 15*28, 26*28))
    return pitch

def pitch_select_upper_half(pitch):
    pitch = pitch.crop((0, 0, 15*28, 13*28))
    return pitch

def create_horizontal_plot(replay_id, match_id, positions, receiving_team, refresh = False):
    append_string = "_kickoff_horizontal.png"
    fname = get_cache_dir() + str(replay_id) + str(match_id) + append_string

    if not os.path.exists(fname) or refresh:
        file_path = resources.files(pkg_name) / "resources" / "nice.jpg"  
        plot = Image.open(file_path)
        plot = plot.resize((26 * 28, 15 * 28))
        plot = add_tacklezones(plot, positions, receiving_team, flip = False, horizontal = True)   
        plot = add_players(plot, positions, receiving_team, flip = False, horizontal = True)
        plot.save(fname,"PNG")
    else:
        plot = Image.open(fname)
    return plot

def create_vertical_plot(replay_id, match_id, positions, receiving_team, refresh = False):
    append_string = "_kickoff_vertical.png"
    fname = get_cache_dir() + str(replay_id) + str(match_id) + append_string

    if not os.path.exists(fname) or refresh:
        file_path = resources.files(pkg_name) / "resources" / "nice.jpg"
        plot = Image.open(file_path)
        plot = plot.rotate(angle = 90, expand = True)
        plot = plot.resize((15 * 28, 26 * 28))
        
        if receiving_team == 'teamAway':
            doFlip = True
        else:
            doFlip = False

        plot = add_tacklezones(plot, positions, receiving_team, flip = doFlip)   
        plot = add_players(plot, positions, receiving_team, flip = doFlip)
        plot.save(fname,"PNG")
    else:
        plot = Image.open(fname)
    return plot

def create_plot(positions, red_team = "teamHome", orientation ='H', crop = "none", skill_bands = False, tackle_zones = False, flip = False, ballpos = None):
    file_path = resources.files(pkg_name) / "resources" / "nice.jpg"
    plot = Image.open(file_path)
    plot = plot.resize((26 * 28, 15 * 28))
    if orientation == 'H':
        if tackle_zones:
            plot = add_tacklezones(plot, positions, red_team, flip = False, horizontal = True)   
        plot = add_players(plot, positions, red_team, flip = False, horizontal = True)
        if skill_bands == True:
            plot = add_skill_bands(plot, positions, flip = False, horizontal = True)
        plot = add_ball(plot, positions, flip = False, horizontal = True, ballpos = ballpos)
  
    elif orientation == 'V': # no ball plotting yet
        plot = plot.rotate(angle = 90, expand = True)
        if tackle_zones:
            plot = add_tacklezones(plot, positions, red_team, flip = flip)   
        plot = add_players(plot, positions, red_team, flip = flip)
        if skill_bands == True:
            plot = add_skill_bands(plot, positions, flip = flip, horizontal = False)
        if crop == 'upper':
            plot = pitch_select_upper_half(plot)
        if crop == 'lower':
            plot = pitch_select_lower_half(plot)            
    else: 
        plot = "unknown plot type"
    return plot

def show_boardpos(rotation = 'H', icon_size = (28, 28), crop = 'none'):
    file_path = resources.files(pkg_name) / "resources" / "nice.jpg"
    pitch = Image.open(file_path)

    icon_w, icon_h = icon_size
    font1 = ImageFont.truetype('LiberationSans-Regular.ttf', 12)
    if rotation == 'V':
        pitch = pitch.rotate(angle = 90, expand = True)
        pitch = pitch.resize((15 * 28, 26 * 28))
        draw = ImageDraw.Draw(pitch)
        for i in range(15):
            for j in range(26):
                text1 = string.ascii_lowercase[i] + str(j+1)
                draw.text((icon_w * (14 - i) + 6, icon_h * j + 7), text = text1, font = font1, fill = 'black')
        if crop == 'upper':
            pitch = pitch_select_upper_half(pitch)
        if crop == 'lower':
            pitch = pitch_select_lower_half(pitch)  
    elif rotation == 'H':
        pitch = pitch.resize((26 * 28, 15 * 28))
        draw = ImageDraw.Draw(pitch)
        for i in range(15):
            for j in range(26):
                text1 = string.ascii_lowercase[i] + str(j+1)
                draw.text((icon_w * j+6,icon_h * i+7), text = text1, font = font1, fill = 'black')
    else:
        pitch = "unknown rotation type"
    return pitch
