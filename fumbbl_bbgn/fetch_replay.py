""" The FUMBBL server, for the replay file API endpoint, uses 'Transfer-Encoding': 'chunked' to "stream" the gzipped content to the client.

From the requests documentation:
```
For chunked encoded responses, it’s best to iterate over the data using Response.iter_content(). In an ideal situation you’ll have set stream=True on the request, in which case you can iterate chunk-by-chunk by calling iter_content with a chunk_size parameter of None. If you want to set a maximum size of the chunk, you can set a chunk_size parameter to any integer.
``` """
import gzip
import time
import requests
import json

def fetch_replay(replay_id, dirname = "raw/replay_files/"):

    #print('fetching replay data for replay_id ' + str(replay_id) + ' as JSON') 
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
