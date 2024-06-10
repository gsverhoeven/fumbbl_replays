""" The FUMBBL server, has an API endpoint to get info about a match.
https://fumbbl.com/apidoc/

"""
import time
import requests
import json
import pandas as pd

def fetch_roster(roster_name = None, ruleset_id = 2228, verbose = False, update = False):
    # check if file already exists, else scrape it
    fname_string = "raw/rosters/rosters_ruleset_" + str(ruleset_id) + ".json"  
    try:
        f = open(fname_string, mode = "rb")

    except OSError as e:
        # scrape it
        ruleset = get_ruleset(ruleset_id, fname_string, verbose)
            
    else:
        # file already present
        if update:
            ruleset = get_ruleset(ruleset_id, fname_string, verbose)
            if verbose:
                print("o",  end = '')
        ruleset = read_json_file(fname_string)

    
    if roster_name is None:
        print("available rosters:")
        for i in range(len(ruleset['rosters'])):
            print(ruleset['rosters'][i]['value'])
        return -1
    else:
        for i in range(len(ruleset['rosters'])):
            if roster_name == ruleset['rosters'][i]['value']:
                roster_id = ruleset['rosters'][i]['id']
                break

    fname_string = "raw/rosters/roster_" + str(roster_id) + ".json"  
    try:
        f = open(fname_string, mode = "rb")
        # check if file already exists, else scrape it

    except OSError as e:
        # scrape it
        roster = get_roster(roster_id, fname_string, verbose = False)
            
    else:
        # file already present
        if update:
            roster = get_roster(roster_id, fname_string, verbose = False)
            if verbose:
                print("o",  end = '')
        roster = read_json_file(fname_string)

    positionId = []
    positionName = []
    shorthand = []
    icon_path = []

    tmpRosters = roster['positions']

    for positionIndex in range(len(tmpRosters)):
        tmpPosition = tmpRosters[positionIndex]
        positionId.append(tmpPosition['id'])
        positionName.append(tmpPosition['title'])
        shorthand.append(tmpPosition['iconLetter'])
        icon_path.append('https://fumbbl.com/i/' + tmpPosition['icon'])

        df_roster = pd.DataFrame( {"positionId": positionId,
                                "positionName": positionName,
                                "shorthand": shorthand,
                                "icon_path": icon_path
                                })

    return df_roster


def get_ruleset(ruleset_id, fname_string, verbose):
    api_string = "https://fumbbl.com/api/ruleset/get/" + str(ruleset_id)

    ruleset = requests.get(api_string)
    ruleset = ruleset.json()

    write_json_file(ruleset, fname_string)
    if verbose:
        print("wrote ruleset", end = '')
    time.sleep(0.3)

    return ruleset

def get_roster(roster_id, fname_string, verbose):
    api_string = "https://fumbbl.com/api/roster/get/" + str(roster_id)

    roster = requests.get(api_string)
    roster = roster.json()

    write_json_file(roster, fname_string)
    if verbose:
        print("wrote roster", end = '')
    time.sleep(0.3)

    return roster

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

def format_roster(roster):
    # return positions file
    return -1

