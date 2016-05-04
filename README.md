# micro-scrabble
Flask web app for playing scrabble with the Raspberry Pi

## Database
Need to use SQLAlchemy database to pass game information around. A game will have its own table that stores everything we need to reinstantiate the `game` class.

| Field | Type | Description |
|:-----:|:----:|:-----------:|
| `game_name` | string | Name of the game |
| `board_matrix` | pickle | Current board state |
| `letters` | pickle | Current tilebag state |
| `dim_r` | int | Number of rows |
| `dim_c` | int | Number of columns |
| `max_rack_letters` | int | Maximum number of letters allowed in player rack |
| `players` | string | Comma delimited string of player names |
| `scores` | pickle | List of integers of player scores |
| `letter_racks` | pickle | List of lists containing players letter racks |

`letter_racks` and `scores` should probably be dictionaries with keys being the player names.
