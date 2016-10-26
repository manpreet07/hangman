# Design of Hangman APIs

###Following properties has been added to Hangman APIs to enhance its features.

- [RandomWords 0.1.5](https://pypi.python.org/pypi/RandomWords/0.1.5) python library is added to the project that is used to generate random words when new game is created.
- History model is added to track the history of the Game played by users.
- Accuracy is added to Score Model to get the players Accuracy of guessing a word. More the guesses are lower the accuracy is
- Additional Endpoints added to get user rankings, game history, and user high scores.
- Game cancel feature is added to Game model so user can cancel their games if they want.
- Game scoring model is added to calculate high scores and rankings etc.

###Some trade-Offs and struggles during the design phase.

- Generating a random word in the code was a bit of struggle that is faced when designing this application, "RamdomWords" a python third party library that generates random words has been added to project to generate random word when user create new game.
