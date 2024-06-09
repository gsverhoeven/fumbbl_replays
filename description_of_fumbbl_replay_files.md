# FUMBBL Replay datafiles: opening up the black box

Replay data is quite verbose and there’s lots of it. The FFB client communicates with the Server using Java Web Sockets.
The raw data packages send over the line are web sockets. 
A replay file would be the json command stream. It’s a complex format, as it’s more or less just logging the data packets between the client and server. 

For example, after unzipping, opening as JSON in VScode and doing autoformatting, we end up with a 266K lines of client server "command" stream.
Each turn is about 10K lines, with roster info at the end.

The high level file format is as follows:

```
{
    "gameStatus": "uploaded",
    "stepStack": {
        "steps": []
    },
    "gameLog": {}, # contains the command stream
    "game": {}, # contains the full roster and position information
    "playerIds": [],
    "swarmingPlayerActual": 0,
    "passState": {},
    "prayerState": {},
    "activeEffects": {}
}
```

I noticed that the replays are really nicely self contained, they contain full copies of the rosters and (if i remember correctly) even ruleset.
Everything in the ruleset that has a bearing on the client
Basically the "client options" tab of the ruleset

A full history of all the events during the game is stored under `gameLog`.

The various phases of the match are clearly distinguished in the command streams.
`turnDataSetTurnNr` , `turnDataSetFirstTurnAfterKickoff`, `gameSetTurnMode`, etc.



## The Field model including the coordinate system

FFB uses a field model that is very straightforward. The 15 x 26 game board is indexed using (X,Y) coordinates, with the top left square being (0,0). 
and the lower right square being (25, 14). 

Players can be either:
* On the pitch
* In the reserve box
* IN the KO box
* In the Badly hurt box
* In the Seriously injured box
* In the RIP box
* In the Ban box
* In The miss next game box

On the pitch the X,Y coordinates are used, the other locations are indexed using -1,-2,-3 etc. 

```
export default class Coordinate {
    x: number;
    y: number;

    public static FIELD_WIDTH = 26;
    public static FIELD_HEIGHT = 15;
    public static RSV_HOME_X = -1;
    public static KO_HOME_X = -2;
    public static BH_HOME_X = -3;
    public static SI_HOME_X = -4;
    public static RIP_HOME_X = -5;
    public static BAN_HOME_X = -6;
    public static MNG_HOME_X = -7;
    public static RSV_AWAY_X = 30;
    public static KO_AWAY_X = 31;
    public static BH_AWAY_X = 32;
    public static SI_AWAY_X = 33;
    public static RIP_AWAY_X = 34;
    public static BAN_AWAY_X = 35;
    public static MNG_AWAY_X = 36;
    
}
```

FFB uses `fieldModelSetPlayerCoordinate` to position players on the field or on the dug out. Players are identified using the FUMBBL player ids. At the end of the replay, all the player information is stored, including extra skills above those that come with the positional, as well as the full rosters (including all possible star players).

## The list of Player states

At any time, each Player is in a particular PlayerState.

```
export default class PlayerState {
    public static UNKNOWN = 0;
    public static STANDING = 1;
    public static MOVING = 2;
    public static PRONE = 3;
    public static STUNNED = 4;
    public static KNOCKED_OUT = 5;
    public static BADLY_HURT = 6;
    public static SERIOUS_INJURY = 7;
    public static RIP = 8;
    public static RESERVE = 9;
    public static MISSING = 10;
    public static FALLING = 11;
    public static BLOCKED = 12;
    public static BANNED = 13;
    public static EXHAUSTED = 14;
    public static BEING_DRAGGED = 15;
    public static PICKED_UP = 16;
    public static HIT_BY_FIREBALL = 17;
    public static HIT_BY_LIGHTNING = 18;
    public static HIT_BY_BOMB = 19;
    public static BIT_ACTIVE = 256;
    public static BIT_CONFUSED = 512;
    public static BIT_ROOTED = 1024;
    public static BIT_HYPNOTIZED = 2048;
    public static BIT_BLOODLUST = 4096;
    public static BIT_USED_PRO = 8192
}
```