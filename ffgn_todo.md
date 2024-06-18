main stuff:
-make parser for blockroll during blitz, 
-pickupproll, leaproll, handover, apothecaryRoll, kick-off table
-use Player State codes 3-7 for injuries

small stuff:
-add activeTeam column
-leave out activate/deactivate (ie coach changed his mind)


-cid 839/840: 2 times same block roll   -> first choice for reroll, then opponent chooses the result. 
-cid845 apo KO becomes stun (playerState 4)

bugs:
-KO/CAS should be ignored when converting to letter-number positions
-KO now is position a32 cid917

checked up until cid978, start turn 5.

testing:
-add test cases 
-Validate on new match https://fumbbl.com/FUMBBL.php?page=match&id=4444067)
-set up venv with requirements.txt (use docker?)
