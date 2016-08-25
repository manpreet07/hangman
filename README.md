#Hangman API


###Endpoints Included:

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
   - Returns: ScoreForms.
   - Description: Returns all Scores recorded by the provided player (unordered). Will raise a NotFoundException if the User does not exist.


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

