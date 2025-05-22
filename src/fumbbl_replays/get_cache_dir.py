import os

def get_cache_dir(dirname = ""):
    home_dir = os.path.expanduser("~")
    cache_dir = home_dir + "/.cache/fumbbl_replays/" + dirname
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir