""" The FUMBBL server, has an API endpoint to get info about a match.
https://fumbbl.com/apidoc/

"""
import time
import requests
import json

def fetch_match(match_id, dirname = "raw/replay_files/", verbose = False):
    # check if file already exists, else scrape it
    fname_string = dirname + str(match_id) + "_match.json"  
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
