# Visualization

We mimic FFB by plotting FFB icons over the pitch.
In python there is Pillow, the Python image library.
This allows manipulating images.

Lets move on to plotting the board state.

We have an empty image of the board as jpg.
We want to plot player icons on it.

First we plot the empty board.
Then we plot a 13 x 26 roster over it.

```
from PIL import Image, ImageDraw, ImageFont
with Image.open("resources/nice.jpg") as pitch:
    display(pitch)
```

Lets find the Player Icons we need.
We look in the rosters.

First we construct a dataFrame with the players of both teams, then we look up the PNG urls from the roster.

# Working with FUMBBL icons

Plot icon on the pitch. 
First grab icon. Then grab pitch. Plot icon on pitch.

```
from urllib.request import urlopen

url = 'https://fumbbl.com/i/645274.png'
icon = Image.open(urlopen(url)).convert("RGBA")
icon_w, icon_h = icon.size
# select first icon
icon = icon.crop((0,0,icon_w/4,icon_w/4))
icon = icon.resize((28, 28))
icon

```

Lets see if we can draw multiple icons on the pitch.

```
pitch = Image.open("resources/nice.jpg")
pitch = pitch.rotate(angle = 90, expand = True)
pitch = pitch.resize((15 * 28, 26 * 28))
pitch_w, pitch_h = pitch.size
icon_w, icon_h = icon.size

for i in range(15):
    pitch.paste(icon, (icon_w * i,icon_h * i), icon)

pitch
```

# Get player positions after kick off

Should check for quick snap etc.
So all position setting up to 'gameSetLastTurnMode' is set to 'setup' and play moves to kick-off phase.

```{python}
df = fb.parse_replay(my_replay) 

positions = df.query('turnNr == 0 & turnMode == "setup" & Half == 1 & \
                     modelChangeId == "fieldModelSetPlayerCoordinate"').groupby('modelChangeKey').tail(1)
```

```
if len(positions.query('PlayerCoordinateX != [-1, 30]')) != 22:
    print("expected 22 players")
else:
    print("22 players on the pitch")

```

```
# select only players on the board at kick-off, i.e. not in reserve
positions = positions.query('PlayerCoordinateX != [-1, 30]').copy()
```

## Transform player positions: rotation and mirroring

After rotating the pitch 90 degrees, A player at (0,0) will be positioned at (14,0), and a player at (25, 14) is now positioned at (0, 25).
So transformation formula is (a,b) becomes (14 - b, a).

```
positions['PlayerCoordinateXrot'] = 14 - positions['PlayerCoordinateY']
positions['PlayerCoordinateYrot'] = positions['PlayerCoordinateX']
```

No we try to mirror the board setup (swap sides). This requires that we shift the y coordinate to the center (+13), then do minus (mirror y position wrt the horizontal middle line) and then shift back.

```
positions['PlayerCoordinateXrot2'] = positions['PlayerCoordinateXrot']
positions['PlayerCoordinateYrot2'] = 25 - positions['PlayerCoordinateYrot']
```

Display all the icon images. Check that they all have 4 columns.
We need the first and third column.
We use the red icons to display offense setups, and blue icons to display defense setups.

Figure out who chooses to receive.
The team that receives is the offensive team, the kicking team set up first and has the defensive.

Looks like the default is `gameSetHomeFirstOffense` set at 0 (i.e. Away has first offense), and only if `gameSetHomeFirstOffense` is set to 1 the home team receives. We use a clunky way to check whether the  `gameSetHomeFirstOffense` command is present during the startGame sequence.

```
display_all_iconsets = 0

if display_all_iconsets:
    for i in range(len(positions)):
        icon_path = positions.iloc[i]['icon_path']
        icon = Image.open(urlopen(icon_path))
        display(icon)
        #print(icon.size)
```