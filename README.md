#Hangman API

###Game Rules

- Hangman APIs currently only support 1 player.
- User can guess a single letter or a whole word.
- If whole word is guessed wrong, the game will be over and user will loose the game.
- If whole word is guesses correct, user wins.
- When new game is created, remaining attempts are set to number of letters in the word. Once all attempts are over, user loose the game.


###Scoring Rules

- Game is scored based on the wins, losses, and accuracy of guesses.
- Accuracy is calculated by diving wins by games played * 100 and divided by guesses.
- Rankings are calculated based on the Accuracy of player.
- When User wins, 2 points per game is added as score in the scoring table.

###Endpoints:

---

#####create_user

   - Path: 'user'
   - Method: POST
   - Parameters: user_name, email (optional)
   - Returns: Message confirming creation of the User.
   - Description: Creates a new User. user_name provided must be unique. Will raise a ConflictException if a User with that user_name already exists.

#####new_game

   - Path: 'game'
   - Method: POST
   - Parameters: user_name
   - Returns: GameForm with initial game state.
   - Description: Creates a new Game. user_name provided must correspond to an existing user - will raise a NotFoundException if not. Also adds a task to a task queue to update the average moves remaining for active games.

#####get_game

   - Path: 'game/{urlsafe_game_key}'
   - Method: GET
   - Parameters: urlsafe_game_key
   - Returns: GameForm with current game state.
   - Description: Returns the current state of a game.

#####make_move

   - Path: 'game/{urlsafe_game_key}'
   - Method: PUT
   - Parameters: urlsafe_game_key, guess
   - Returns: GameForm with new game state.
   - Description: Accepts a 'guess' and returns the updated state of the game. If this causes a game to end, a corresponding Score entity will be created.

#####get_scores

   - Path: 'scores'
   - Method: GET
   - Parameters: None
   - Returns: ScoreForms.
   - Description: Returns all Scores in the database (unordered).

#####get_user_scores

   - Path: 'scores/user/{user_name}'
   - Method: GET
   - Parameters: user_name
   - Returns: GameForms.
   - Description: Returns all Scores recorded by the provided player (unordered). Will raise a NotFoundException if the User does not exist.

#####get_average_attempts_remaining

   - Path: 'games/{urlsafe_game_key}/average_attempts'
   - Method: GET
   - Parameters: urlsafe_game_key
   - Returns: GameForm.
   - Description: Returns average attempts remaining for the game that is in progress.
   
#####get_user_games

   - Path: 'scores/user/{user_name}/games'
   - Method: GET
   - Parameters: user_name
   - Returns: GameForms.
   - Description: Returns all Active Games recorded by the provided player.
   
#####cancel_game

   - Path: 'games/{urlsafe_game_key}/cancel_game'
   - Method: PUT
   - Parameters: urlsafe_game_key
   - Returns: GameForm.
   - Description: Returns Game cancelled by the provided player.
   
#####get_high_scores

   - Path: 'scores/high_scores'
   - Method: GET
   - Parameters: not required
   - Returns: ScoreForms.
   - Description: Returns High Scores of all the players.
   
#####get_user_rankings

   - Path: 'scores/rankings'
   - Method: GET
   - Parameters: not required
   - Returns: ScoreForms.
   - Description: Returns User Rankings by accuracy.
   
#####get_game_history

   - Path: 'games/{urlsafe_game_key}/history'
   - Method: GET
   - Parameters: urlsafe_game_key
   - Returns: HistoryForms.
   - Description: Returns history of the game in progress.
   
###Models Included:

---

#####User

- Stores unique user_name and (optional) email address.

#####Game

- Stores unique game states. Associated with User model via KeyProperty.

#####Score

- Records completed games. Associated with Users model via KeyProperty.

###Forms Included:

#####GameForm

- Representation of a Game's state (urlsafe_key, attempts_remaining, game_over flag, message, user_name, progress, letters used).

#####HistoryForm

- Representation of a Game's history (date time, guess, result).

#####NewGameForm

- Used to create a new game (user_name)

#####MakeMoveForm

- Inbound make move form (guess).

#####ScoreForm

- Representation of a completed game's Score (user_name, date, games played, games won).

#####ScoreForms

- Multiple ScoreForm container.

#####StringMessage

- General purpose String container.

#####HistoryForms

- Multiple HistoryForm container.