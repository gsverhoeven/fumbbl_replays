from fumbbl_replays import fetch_replay

result_vector = []

test_matches = [4407782, 4538795]
testdir = "example_input/"

for i in range(len(test_matches)):
    test_match_id = test_matches[i]
    # works with fetch_match, need both both a local match and a local replay file
    my_replay = fetch_replay(match_id = test_match_id, dirname = testdir, verbose = False)
    my_gamelog = my_replay['game'] 
    result_vector.append((my_gamelog['turnMode'] == 'endGame'))

def test_fetch_replay():
    assert result_vector == [True, True]