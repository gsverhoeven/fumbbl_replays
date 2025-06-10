import os
from PIL import Image
from math import ceil
from IPython.display import display

def select_images(df_replays, race_name_defense, race_name_offense_list):
    im_list = []
    for i in range(len(df_replays)):
        if df_replays.iloc[i]['raceDefense'] == race_name_defense:
            if df_replays.iloc[i]['raceOffense'] in race_name_offense_list:
                dirname = "kickoff_pngs/" + df_replays.iloc[i]['raceDefense'] + "/"
                dirname = dirname.lower()
                dirname = dirname.replace(' ', '_')
                fname = dirname + str(df_replays.iloc[i]['replayId']) + "_" + \
                    str(df_replays.iloc[i]['matchId']) + "_kickoff_lower_defense.png" 
                #print(fname)
                if os.path.isfile(fname):
                    my_im = Image.open(fname)
                    im_list.append(my_im)
    return im_list

def make_tiling(im_list, h = 2,  scale = 1.0):
    im1 = im_list[0]
    v = ceil(len(im_list) / h)
    dst = Image.new(mode = 'RGB', size = (im1.width * h, im1.height * v),  color = (153, 153, 153))
    n_im = 0
    for hc in range(h):
        for vc in range(v):
            if n_im >= len(im_list):
                pass
            else:
                dst.paste(im_list[n_im], (im1.width * hc , im1.height * vc))
            n_im = n_im + 1
    
    dst = dst.resize(size = (ceil(dst.width * scale), ceil(dst.height * scale)) )

    return display(dst)