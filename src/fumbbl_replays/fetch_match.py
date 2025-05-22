""" The FUMBBL server, has an API endpoint to get info about a match.
https://fumbbl.com/apidoc/

"""
import time
import requests
import json
import os
from .get_cache_dir import get_cache_dir

def fetch_match(match_id, dirname = "raw/replay_files/", verbose = False):
    cache_dir = get_cache_dir(dirname)

    # check if file already exists, else scrape it
    fname_string = cache_dir + str(match_id) + "_match.json"  
    try:
        f = open(fname_string, mode = "rb")

    except OSError as e:
        # scrape it
        api_string = "https://fumbbl.com/api/match/get/" + str(match_id)

        match = requests.get(api_string)
        match = match.json()

        write_json_file(match, fname_string)
        if verbose:
            print("x", end = '')
        time.sleep(0.3)
            
    else:
        # file already present
        if verbose:
            print("o",  end = '')
        match = read_json_file(fname_string)

    return match

def fetch_team_matches(team_id, dirname = "raw/replay_files/", verbose = False):
    
    api_string = "https://fumbbl.com/api/team/matches/" + str(team_id)
    finished = 0
    iteration = 0

    while finished == 0:
        team_batch = fetch_batch(team_id, api_string, dirname, iteration, verbose)

        if len(team_batch) < 25:
            finished = 1
            if iteration == 0:
                team_matches = team_batch
            else:
                team_matches = team_matches + team_batch
        else:
            if iteration == 0:
                team_matches = team_batch
            else:
                team_matches = team_matches + team_batch
            iteration += 1
            api_string = "https://fumbbl.com/api/team/matches/" + str(team_id) + "/" + str(team_batch[24]['id']-1)

    return team_matches

def fetch_batch(team_id, api_string, dirname, iteration, verbose):
    home_dir = os.path.expanduser("~")
    cache_dir = home_dir + "/.cache/fumbbl_replays/" + dirname
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # check if file already exists, else scrape it
    if iteration == 0:
        fname_string = cache_dir + str(team_id) + "_team_matches.json"  
    else:
        fname_string = cache_dir + str(team_id) + "_" + str(iteration) + "_team_matches.json"  
    try:
        f = open(fname_string, mode = "rb")

    except OSError as e:
        # scrape it
        team_matches = requests.get(api_string)
        team_matches = team_matches.json()

        write_json_file(team_matches, fname_string)
        if verbose:
            print("x", end = '')
        time.sleep(0.3)
            
    else:
        # file already present
        if verbose:
            print("o",  end = '')
        team_matches = read_json_file(fname_string)

    return team_matches

def write_json_file(json_object, fname = None):
    if fname is None:
        return "fname missing"
    with open(fname, mode = "w", encoding='UTF-8') as f:
        f.write(json.dumps(json_object, ensure_ascii = False, indent = 4))

def read_json_file(fname):

    if fname is None:
        return "fname missing"

    with open(fname, mode = "r", encoding='UTF-8') as f:
        json_object = json.load(f)

    return json_object
