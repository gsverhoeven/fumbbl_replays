# Introducing the fumbbl_replays Python package

The `fumbbl_replays` Python package is about analyzing FUMBBL game logs for the board game Blood Bowl.
On the FUMBBL website, a lot of high quality replay data is available as well as an API to conveniently fetch the data.
In addition, the API provides up to date roster information.
To use do useful analyses (aka nufflytics) in Python with this data, we need a utility package / library.
In R, a similar package exists to work with BB2 replays [https://github.com/nufflytics/nufflytics].
To my knowledge, no work has been done yet on BB3 replay files.

We also need a standard way to describe Blood Bowl games in a compact way, that is both human and machine readable.
In chess, there is the **Portable Game Notation (PGN)**. PGN has become the de facto standard of describing Chess games.
For Blood Bowl, already in 2002 some work has been done towards this end. David Morgan-Mar developed a notation for the purpose of sharing game logs over the internet. [https://www.dangermouse.net/games/bloodbowl/rules.html]

If we could converge on a standard Fantasy Football Game Notation, it would serve many purposes:
* It would allow us to interchange data between software
* it would help to train AI engines.

So the package is being developed with this end goal in mind. As Blood Bowl is a much complexer game than Chess, we need some intermediate goals that bring us closer to the end goal. Thus, I started with extracting FUMBBL board positions, plotting board positions using a short hand notation for board pieces (players) and codifying player moves.


```python
%pip install -e . --quiet
```

    [33mWARNING: You are using pip version 21.2.4; however, version 21.3.1 is available.
    You should consider upgrading via the '/home/gertjan/venvs/requests_env/bin/python -m pip install --upgrade pip' command.[0m
    Note: you may need to restart the kernel to use updated packages.


# Plotting Blood Bowl board positions

If we want to describe a board state, we need to describe the pieces, and we need to describe the location of the pieces.
(We also need to describe the "state" of the pieces, as players can be either standing, prone, or stunned, and can be in various special states such as "Bone head", "Rooted", "Hypnotized" etc. A full game state also contains additional information on rerolls, players on the bench etc. This is not yet implemented)

Let's start with the location of the pieces. A grid reference system is needed.
The game board of Blood Bowl has dimensions 15 x 26.
It has cognitive benefit to use numbers for one dimension, and letters for the other dimensions. Fancy word: alphanumeric.
Chess over the centuries has had various notations, and this notation is the one that became universally accepted.
[https://en.wikipedia.org/wiki/Algebraic_notation_(chess)]
The only choice left for us is then, which axis should have letters, and which axis should have the numbers.

A strong argument was made on the BotBowl discord that distance to the end zone is very important in BB.
By using numbers for the long axis, we can easily deduce that a Gutter Runner at position c15 is in scoring position: It needs 11 movement to score a touchdown at c26.
This notation is also used by Cow Daddy Gaming in his "What´s the play" puzzles.

I wrote a function `show_boardpos()` that displays the name of all the board positions.



```python
import fumbbl_replays as fb

fb.show_boardpos(rotation = 'H')
```




    
![png](fumbbl_replays_files/fumbbl_replays_3_0.png)
    



Next is that we need a way to describe the playing pieces, and visualize them. In chess it is easy, there are only six different ones.
In Blood Bowl, there are roughly 200 different playing pieces (30 teams, times 5 positionals, plus 50+ star players).
Here the concept of a roster can help us out. 
I wrote a function `fetch_roster()` that fetches rosters from FUMBBL and displays the positions.
It also contains links to icons that can represent the piece on the board.
Take for example the High Elf roster.


```python
roster = fb.fetch_roster("High Elf")
roster
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>positionId</th>
      <th>positionName</th>
      <th>shorthand</th>
      <th>icon_path</th>
      <th>race</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>39330</td>
      <td>Lineman</td>
      <td>L</td>
      <td>https://fumbbl.com/i/585638.png</td>
      <td>High Elf</td>
    </tr>
    <tr>
      <th>1</th>
      <td>39331</td>
      <td>Thrower</td>
      <td>T</td>
      <td>https://fumbbl.com/i/436284.png</td>
      <td>High Elf</td>
    </tr>
    <tr>
      <th>2</th>
      <td>39332</td>
      <td>Catcher</td>
      <td>C</td>
      <td>https://fumbbl.com/i/585639.png</td>
      <td>High Elf</td>
    </tr>
    <tr>
      <th>3</th>
      <td>39333</td>
      <td>Blitzer</td>
      <td>Z</td>
      <td>https://fumbbl.com/i/436286.png</td>
      <td>High Elf</td>
    </tr>
  </tbody>
</table>
</div>



It has four different pieces or "positionals". It turns out that FUMBBL has already solved our problem of denoting them, introducing a shorthand text reference. 
So if we want to describe some action involving a High Elf Catcher, and there are four of them on the board, we could denote them by C1, C2, C3 and C4.
This is compact, and has meaning within the context of the High Elf roster.

If we combine the descriptions of the pieces, and their location, we have enough to describe for example an initial setup formation before kick-off.


```python
roster = fb.fetch_roster("High Elf")

my_setup = ['setup', ['L1: g13', 'L2: h13', 'L3: i13', 'Z1: c11', 'Z2: m11', 'T1: h6', 'L4: e11', 
                      'L5: k11', 'C1: l10', 'C2: d10', 'L6: h11']]
```

I wrote a function `create_position()` that combines the roster and the setup annotation to create an object that contains all the information to make a nice plot of the board state. The function `print_position()` prints a nicely formatted summary of the position.
As default, a position is created for the home team, denoted as "teamHome".


```python
positions = fb.create_position(roster, my_setup)
fb.print_position(positions)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>home_away</th>
      <th>race</th>
      <th>short_name</th>
      <th>positionName</th>
      <th>boardpos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>T1</td>
      <td>Thrower</td>
      <td>h6</td>
    </tr>
    <tr>
      <th>9</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>C2</td>
      <td>Catcher</td>
      <td>d10</td>
    </tr>
    <tr>
      <th>8</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>C1</td>
      <td>Catcher</td>
      <td>l10</td>
    </tr>
    <tr>
      <th>3</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>Z1</td>
      <td>Blitzer</td>
      <td>c11</td>
    </tr>
    <tr>
      <th>6</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>L4</td>
      <td>Lineman</td>
      <td>e11</td>
    </tr>
    <tr>
      <th>10</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>L6</td>
      <td>Lineman</td>
      <td>h11</td>
    </tr>
    <tr>
      <th>7</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>L5</td>
      <td>Lineman</td>
      <td>k11</td>
    </tr>
    <tr>
      <th>4</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>Z2</td>
      <td>Blitzer</td>
      <td>m11</td>
    </tr>
    <tr>
      <th>0</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>L1</td>
      <td>Lineman</td>
      <td>g13</td>
    </tr>
    <tr>
      <th>1</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>L2</td>
      <td>Lineman</td>
      <td>h13</td>
    </tr>
    <tr>
      <th>2</th>
      <td>teamHome</td>
      <td>High Elf</td>
      <td>L3</td>
      <td>Lineman</td>
      <td>i13</td>
    </tr>
  </tbody>
</table>
</div>



Let's suppose that the High Elf team is playing against a Gnome team. Let's also fetch a Gnome roster and create a board position on the other half of the pitch.
As we already have a home team, we refer to this team as "teamAway".


```python
roster = fb.fetch_roster("Gnome")

my_setup = ['setup', ['T2: j14', 'T1: f14', 'F1: h20', 'I1: b14', 'I2: n14', 'L3: e14', 'L6: k14', 
                      'B2: m15', 'B1: c15', 'L4: g15', 'F2: i16']]

positions2 = fb.create_position(roster, my_setup, 'teamAway')

fb.print_position(positions2)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>home_away</th>
      <th>race</th>
      <th>short_name</th>
      <th>positionName</th>
      <th>boardpos</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>3</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>I1</td>
      <td>Gnome Illusionist</td>
      <td>b14</td>
    </tr>
    <tr>
      <th>5</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>L3</td>
      <td>Gnome Lineman</td>
      <td>e14</td>
    </tr>
    <tr>
      <th>1</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>T1</td>
      <td>Altern Forest Treeman</td>
      <td>f14</td>
    </tr>
    <tr>
      <th>0</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>T2</td>
      <td>Altern Forest Treeman</td>
      <td>j14</td>
    </tr>
    <tr>
      <th>6</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>L6</td>
      <td>Gnome Lineman</td>
      <td>k14</td>
    </tr>
    <tr>
      <th>4</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>I2</td>
      <td>Gnome Illusionist</td>
      <td>n14</td>
    </tr>
    <tr>
      <th>8</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>B1</td>
      <td>Gnome Beastmaster</td>
      <td>c15</td>
    </tr>
    <tr>
      <th>9</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>L4</td>
      <td>Gnome Lineman</td>
      <td>g15</td>
    </tr>
    <tr>
      <th>7</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>B2</td>
      <td>Gnome Beastmaster</td>
      <td>m15</td>
    </tr>
    <tr>
      <th>10</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>F2</td>
      <td>Woodland Fox</td>
      <td>i16</td>
    </tr>
    <tr>
      <th>2</th>
      <td>teamAway</td>
      <td>Gnome</td>
      <td>F1</td>
      <td>Woodland Fox</td>
      <td>h20</td>
    </tr>
  </tbody>
</table>
</div>



As a final step before plotting, we add both positions together.
As both are `pandas` DataFrames, we use the `concat()` function from `pandas`  to combine ("concatenate") them.


```python
import pandas as pd

positions = pd.concat([positions, positions2])
```

The function `create_plot()` plots the board position.
By default, it plots a horizontal pitch, with the team denoted as "teamHome" in red, and the other team in blue.


```python
fb.create_plot(positions)
```




    
![png](fumbbl_replays_files/fumbbl_replays_16_0.png)
    



The `create_plot()` function allows us the swap the color of the teams, to change the pitch orientation to vertical, and to add a layer of semi-transparant tacklezones.


```python
fb.create_plot(positions, red_team = "teamAway", orientation = 'V', tackle_zones = True)
```




    
![png](fumbbl_replays_files/fumbbl_replays_18_0.png)
    



The library also support moving single pieces (players). It currently only works for pieces that already exist in a board position.
In the plot above, suppose we want to move the Woodland Fox F1 to board position `o26`:


```python
positions = fb.move_piece(positions, "teamAway", "F1", "o26")

fb.create_plot(positions, red_team = "teamAway")
```




    
![png](fumbbl_replays_files/fumbbl_replays_20_0.png)
    



# Plotting board positions from FUMBBL replays

Up until now, we created board positions from scratch, using rosters from FUMBBL and a simple way to describe a board position.
The package also allows us to plot board positions extracted from FUMBBL replay files.
At this moment, only the board position right before kick-off can be plotted.
Suppose we want to plot this position for [match 4551601](https://www.fumbbl.com/p/match?id=4551601).

We first need to fetch the replay data. The `fetch_data()` function takes the `match_id` as argument and returns five objects:
the `match_id`, `replay_id`, a `positions` object, which team is the `receiving_team` (i.e. playing offense), and a `metadata` list (coach names, race names, and match touchdown result).


```python
match_id, replay_id, positions, receiving_team, metadata = fb.fetch_data(match_id = 4543460)
```

To plot the board state right before kick-off, we can use the `create_plot()` function in the same way as above.
We plot the receiving team in red so we can see which team is playing offense and which team is playing defense.


```python
fb.create_plot(positions, red_team = receiving_team)
```




    
![png](fumbbl_replays_files/fumbbl_replays_24_0.png)
    



Adjusting this board position by moving players one-by-one works also in the same way as above.


```python
positions = fb.move_piece(positions, "teamHome", "Z1", "b26")
positions = fb.move_piece(positions, "teamHome", "Z2", "o26")

fb.create_plot(positions, red_team = receiving_team)
```




    
![png](fumbbl_replays_files/fumbbl_replays_26_0.png)
    



Suppose we think that the offensive setup is awesome, and we wish to share this setup with other coaches.
Here the compact way to describe a setup using player abbreviations and the alphanumeric grid system comes in handy.
To get the position in this notation I wrote the function `get_position()`.



```python
fb.get_position(positions, home_away = 'teamAway')

```

    ['setup', ['T1: j14', 'T2: f14', 'B1: g14', 'B2: i14', 'L1: h14', 'I1: b15', 'I2: n15', 'L4: l14', 'L3: d14', 'L2: k14', 'F2: h20']]


Suppose we think this setup is awesome, but it would be even better if the illusionist in row `b` would be a second Woodland Fox.
We can take the setup (copy-paste), change the setup slightly, and create a new position.
As we now only have a single team, we can rotate the pitch and crop to show only the upper part of it.


```python
roster = fb.fetch_roster("Gnome")

my_setup = ['setup', ['T1: j14', 'T2: f14', 'B1: g14', 'B2: i14', \
                      'L1: h14', 'F1: b15', 'I2: n15', 'L4: l14', \
                        'L3: d14', 'L2: k14', 'F2: h20']]

positions = fb.create_position(roster, my_setup)

fb.create_plot(positions, orientation= "V", crop = "lower")
```




    
![png](fumbbl_replays_files/fumbbl_replays_30_0.png)
    



# Working with raw replays directly

It is also possible to work with the raw FUMBBL replay files directly.
I made a start with describing the file format in `doc/fumbbl_replay_file_format.md`.
We can use `fetch_replay()` to retrieve a replay in JSON format.
JSON consists of key-value pairs.
We can for example query the value of the key `gameStatus`:


```python
my_replay = fb.fetch_replay(match_id = 4447439)
my_replay['gameStatus']
```




    'uploaded'



The replay contains both a game log, as well as full roster information on both teams.
We can extract the roster information from the replay using the function `extract_rosters_from_replay()`.



```python
pd.set_option('display.max_colwidth', None)

df_positions = fb.extract_rosters_from_replay(my_replay)
(df_positions
 .query("home_away == 'teamAway'")
 .filter(['short_name', 'positionName', 'skillArray'])
)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>short_name</th>
      <th>positionName</th>
      <th>skillArray</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Tr1</td>
      <td>Loren Forest Treeman</td>
      <td>[Loner, Mighty Blow, Stand Firm, Strong Arm, Take Root, Thick Skull, Throw Team-Mate]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>W1</td>
      <td>Wardancer</td>
      <td>[Block, Dodge, Leap]</td>
    </tr>
    <tr>
      <th>2</th>
      <td>W2</td>
      <td>Wardancer</td>
      <td>[Strip Ball, Block, Dodge, Leap]</td>
    </tr>
    <tr>
      <th>3</th>
      <td>T1</td>
      <td>Thrower</td>
      <td>[Leader, Pass]</td>
    </tr>
    <tr>
      <th>4</th>
      <td>C1</td>
      <td>Catcher</td>
      <td>[Catch, Dodge]</td>
    </tr>
    <tr>
      <th>5</th>
      <td>C2</td>
      <td>Catcher</td>
      <td>[Catch, Dodge]</td>
    </tr>
    <tr>
      <th>6</th>
      <td>L1</td>
      <td>Wood Elf Lineman</td>
      <td>[Dodge]</td>
    </tr>
    <tr>
      <th>7</th>
      <td>L2</td>
      <td>Wood Elf Lineman</td>
      <td>[Dodge]</td>
    </tr>
    <tr>
      <th>8</th>
      <td>L3</td>
      <td>Wood Elf Lineman</td>
      <td>[]</td>
    </tr>
    <tr>
      <th>9</th>
      <td>L4</td>
      <td>Wood Elf Lineman</td>
      <td>[Wrestle]</td>
    </tr>
    <tr>
      <th>10</th>
      <td>L5</td>
      <td>Wood Elf Lineman</td>
      <td>[Wrestle]</td>
    </tr>
  </tbody>
</table>
</div>



I wrote a replay parser that parses the gameLog section of a replay and transforms this into a `pandas` DataFrame object, i.e. a flat 2D table with rows and columns.


```python
df = fb.parse_replay(my_replay)
(df[0:4]
 .filter(['commandNr', 'turnNr', 'turnMode', 'Half', 'modelChangeId', 'modelChangeValue'])
)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>commandNr</th>
      <th>turnNr</th>
      <th>turnMode</th>
      <th>Half</th>
      <th>modelChangeId</th>
      <th>modelChangeValue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>0</td>
      <td>startGame</td>
      <td>0</td>
      <td>fieldModelAddPlayerMarker</td>
      <td>{'playerId': '15440786', 'homeText': 'B', 'awayText': 'B'}</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>0</td>
      <td>startGame</td>
      <td>0</td>
      <td>fieldModelAddPlayerMarker</td>
      <td>{'playerId': '15440787', 'homeText': 'G', 'awayText': 'G'}</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>0</td>
      <td>startGame</td>
      <td>0</td>
      <td>fieldModelAddPlayerMarker</td>
      <td>{'playerId': '15440788', 'homeText': 'G', 'awayText': 'G'}</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>0</td>
      <td>startGame</td>
      <td>0</td>
      <td>fieldModelAddPlayerMarker</td>
      <td>{'playerId': '15440790', 'homeText': 'G', 'awayText': 'G'}</td>
    </tr>
  </tbody>
</table>
</div>



We can use the `pandas` `query()` function to select rows based on conditions.
This query selects all "fieldModelSetPlayerCoordinate" commands during setup before turn 1.


```python
positions = (df.query('turnNr == 0 & turnMode == "setup" & Half == 1 & \
                     modelChangeId == "fieldModelSetPlayerCoordinate"')
                     .groupby('modelChangeKey')
                     .tail(1))

(positions[0:4]
 .filter(['commandNr', 'turnNr', 'turnMode', 'Half', 'modelChangeId', 'modelChangeValue'])
)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>commandNr</th>
      <th>turnNr</th>
      <th>turnMode</th>
      <th>Half</th>
      <th>modelChangeId</th>
      <th>modelChangeValue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>77</th>
      <td>20</td>
      <td>0</td>
      <td>setup</td>
      <td>1</td>
      <td>fieldModelSetPlayerCoordinate</td>
      <td>[12, 6]</td>
    </tr>
    <tr>
      <th>79</th>
      <td>21</td>
      <td>0</td>
      <td>setup</td>
      <td>1</td>
      <td>fieldModelSetPlayerCoordinate</td>
      <td>[12, 7]</td>
    </tr>
    <tr>
      <th>81</th>
      <td>22</td>
      <td>0</td>
      <td>setup</td>
      <td>1</td>
      <td>fieldModelSetPlayerCoordinate</td>
      <td>[12, 8]</td>
    </tr>
    <tr>
      <th>84</th>
      <td>24</td>
      <td>0</td>
      <td>setup</td>
      <td>1</td>
      <td>fieldModelSetPlayerCoordinate</td>
      <td>[10, 4]</td>
    </tr>
  </tbody>
</table>
</div>



As I was interested in **defensive** setup formations, I wrote a function `determine_receiving_team_at_start()` that does exactly what you'd expect given its name :)


```python
fb.determine_receiving_team_at_start(df)
```




    'teamAway'



# Towards FFGN

Finally, there is a function `fumbbl2ffgn()` that is very much a work in progress.
The idea is to take a FUMBBL game log, and systematically strip away all information that is redundant regarding the actual logging of what happened during the game. A minimal game description would consist of all actions taken, all decisions that were made (i.e. to use the dodge skill) and all dice results.
After we have such a description, we can transform it to a compact annotation that is readable both by humans and machines, and is still a complete description of the game, in that the full game can be reproduced.
The compact annotation would then be candidate to become the official "Fantasy Football Game Notation", or FFGN for short.


```python
my_game_log = fb.fumbbl2ffgn(match_id = 4447439)
len(my_game_log)
```




    866



This is where it currently stands. A single gamelog is now roughly 1000 lines of text.
The table below describes the first turn of a Wood Elf team against Necromantic.


```python
pd.set_option('display.max_colwidth', None)

# Turn 1 for the offensive
(my_game_log
 .query("Half == 1 & turnNr == 1 & commandNr > 88 & commandNr < 211")
 .filter(['modelChangeKey', 'modelChangeValue'])
)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>modelChangeKey</th>
      <th>modelChangeValue</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>29</th>
      <td>['T1']</td>
      <td>[j17, i17, h17, g17, f17, e17]</td>
    </tr>
    <tr>
      <th>30</th>
      <td>['C1']</td>
      <td>[g17, f17, e18, d17, c17, b17]</td>
    </tr>
    <tr>
      <th>31</th>
      <td>['L1']</td>
      <td>[d14, e13, f13]</td>
    </tr>
    <tr>
      <th>32</th>
      <td>['L4']</td>
      <td>Block roll:['!', '!'] | block result: ! (POW/PUSH)</td>
    </tr>
    <tr>
      <th>33</th>
      <td>['L5']</td>
      <td>[g12]</td>
    </tr>
    <tr>
      <th>34</th>
      <td>['L4']</td>
      <td>[g13]</td>
    </tr>
    <tr>
      <th>35</th>
      <td>0</td>
      <td>Armour roll: [3, 5] | Armour of ['L5'] is not broken</td>
    </tr>
    <tr>
      <th>36</th>
      <td>['Tr1']</td>
      <td>Confusion roll: 2 | ['Tr1'] acts normally</td>
    </tr>
    <tr>
      <th>37</th>
      <td>['Tr1']</td>
      <td>Block roll:['&gt;', '%', '*'] | block result: * (POW)</td>
    </tr>
    <tr>
      <th>38</th>
      <td>['L2']</td>
      <td>[i12]</td>
    </tr>
    <tr>
      <th>39</th>
      <td>['Tr1']</td>
      <td>[h13]</td>
    </tr>
    <tr>
      <th>40</th>
      <td>0</td>
      <td>Armour roll: [4, 2] | Armour of ['L2'] is not broken</td>
    </tr>
    <tr>
      <th>41</th>
      <td>['L5']</td>
      <td>Block roll:['&gt;', '!'] | block result: ! (POW/PUSH)</td>
    </tr>
    <tr>
      <th>42</th>
      <td>['L4']</td>
      <td>[h12]</td>
    </tr>
    <tr>
      <th>43</th>
      <td>0</td>
      <td>Armour roll: [2, 5] | Armour of ['L4'] is not broken</td>
    </tr>
    <tr>
      <th>44</th>
      <td>['L3']</td>
      <td>[m16, l16, k16, j16, i16, h16]</td>
    </tr>
    <tr>
      <th>45</th>
      <td>['L2']</td>
      <td>[l15, k15, j15, i15, h15, g15, f15]</td>
    </tr>
    <tr>
      <th>46</th>
      <td>['C2']</td>
      <td>[c15]</td>
    </tr>
    <tr>
      <th>47</th>
      <td>['W1']</td>
      <td>[d16, c16, b16]</td>
    </tr>
    <tr>
      <th>48</th>
      <td>['W2']</td>
      <td>[g18, f18, e18, d18, c18, b18]</td>
    </tr>
    <tr>
      <th>49</th>
      <td>['W2']</td>
      <td>{'reportId': 'pickUpRoll', 'playerId': '['W2']', 'successful': True, 'roll': 4, 'minimumRoll': 2, 'reRolled': False}</td>
    </tr>
    <tr>
      <th>50</th>
      <td>['W2']</td>
      <td>[c18, d18]</td>
    </tr>
    <tr>
      <th>51</th>
      <td>___</td>
      <td>End of Turn</td>
    </tr>
  </tbody>
</table>
</div>



*Thrower 1 moves. Catcher 1 moves. Lineman 1 moves. Lineman 4 blocks, chooses pow/push, pows Zombie lineman L5 into square g12, follows up, does not break armor.*
*Treeman does not take root, does a 3D block on Zombie lineman 2, chooses pow into square i12, follows up to square h13, does not break armor.*
*Lineman 5 blocks zombie lineman L4, pows into h12, does not follow up, does not break armor. Then linemen L3, L2, catcher C2 and wardancer W1 all do a move action.*
*Finally Wardancer W2 moves, picks up the ball and moves a bit more. End turn.*
