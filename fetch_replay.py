def fetch_replay(replay_id):

    #print('fetching replay data for replay_id ' + str(replay_id) + ' as JSON')

    dirname = "raw/replay_files/" 
    fname_string_gz = dirname + str(replay_id) + ".gz"        

    # check if file already exists, else scrape it
    try:
        f = open(fname_string_gz, mode = "rb")
    except OSError as e:
        # scrape it 
        api_string = "https://fumbbl.com/api/replay/get/" + str(replay_id) + "/gz" 

        replay = requests.get(api_string, stream = True)
        print("x",  end = '')
        with open(fname_string_gz, 'wb') as f:
            for chunk in replay.iter_content(None):
                f.write(chunk)
        time.sleep(0.3)
        with gzip.open(fname_string_gz, mode = "rb") as f:
            replay = json.load(f)
            
    else:
        # file already present
        print("o",  end = '')
        with gzip.open(fname_string_gz, mode = "rb") as f:
            replay = json.load(f)

    return replay
