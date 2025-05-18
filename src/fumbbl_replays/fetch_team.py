""" The FUMBBL server, has an API endpoint to get info about a team.
https://fumbbl.com/apidoc/

"""
import time
import requests
import json
import os

def fetch_team(team_id, verbose = False):
    home_dir = os.path.expanduser("~")
    cache_dir = home_dir + "/.cache/fumbbl_replays/teams/"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # check if file already exists, else scrape it
    fname_string = cache_dir + str(team_id) + "_team.json"  
    try:
        f = open(fname_string, mode = "rb")

    except OSError as e:
        # scrape it
        api_string = "https://fumbbl.com/api/team/get/" + str(team_id)

        team = requests.get(api_string)
        team = team.json()

        write_json_file(team, fname_string)
        if verbose:
            print("x", end = '')
        time.sleep(0.3)
            
    else:
        # file already present
        if verbose:
            print("o",  end = '')
        team = read_json_file(fname_string)

    return team

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
