from fumbbl_replays.parse_confusionroll import parse_confusionroll
import json

obj = '{"reportId": "confusionRoll", "playerId": "15064977", "successful": true, "roll": 2, "minimumRoll": 2, "reRolled": false, "confusionSkill": "Bone Head"}'

obj = json.loads(obj)
out = parse_confusionroll(obj)

desired_out = 'Confusion roll: 2 | 15064977 acts normally'

def test_parse_confusionroll():
    assert out == desired_out
