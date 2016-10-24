"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

from datetime import date
from protorpc import messages, message_types
from google.appengine.ext import ndb
import datetime

from random_words import RandomWords


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True)
    progress = ndb.StringProperty(repeated=True)
    letters_used = ndb.StringProperty(repeated=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    game_canceled = ndb.BooleanProperty(required=True, default=False)

    @classmethod
    def new_game(cls, user):

        """Creates and returns a new game"""
        rw = RandomWords()
        RANDOM_WORD = rw.random_word()

        _progress = ['_'] * len(RANDOM_WORD)
        _letters_used = ['_'] * len(RANDOM_WORD)

        game = Game(user=user,
                    target=RANDOM_WORD,
                    attempts_allowed=len(RANDOM_WORD),
                    attempts_remaining=len(RANDOM_WORD),
                    progress=_progress,
                    letters_used=_letters_used,
                    game_over=False,
                    game_canceled=False)
        game.put()
        return game

    def cancel_the_game(self):
        """Cancel the game."""
        self.game_canceled = True
        self.put()

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = message
        form.progress = self.progress
        form.lettersUsed = self.letters_used
        form.game_canceled = self.game_canceled
        return form

    def post_transaction(self, guess, result):
        history = History(game=self.key, guess=guess, result=result)
        history.put()
        return history

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()
        # Update Score
        if won:
            score = Score(user=self.user, date=date.today(),
                          guesses=self.attempts_allowed - self.attempts_remaining)
            score.games_played += 1
            score.games_won += 1
        else:
            score = Score(user=self.user, date=date.today(),
                          guesses=self.attempts_allowed - self.attempts_remaining)
            score.games_played += 1
        score.winning_percentage = (score.games_won / score.games_played) * 100
        score.put()

    def game_status(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.message = message
        form.attempts_remaining = self.attempts_remaining
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.game_over = self.game_over
        form.game_canceled = self.game_canceled
        return form


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)
    games_played = ndb.IntegerProperty(default=0,required=True)
    games_won = ndb.IntegerProperty(default=0,required=True)
    winning_percentage = ndb.IntegerProperty(default=0)

    def get_score(self):
        return ScoreForm(user_name=self.user.get().name, games_played=self.games_played, games_won=self.games_won)

    def get_ranking(self):
        return ScoreForm(user_name=self.user.get().name, winning_percentage=self.winning_percentage)


class History(ndb.Model):
    """History object"""
    date_time = ndb.DateTimeProperty(auto_now_add=True)
    game = ndb.KeyProperty(required=True, kind='Game')
    guess = ndb.StringProperty(required=True)
    result = ndb.StringProperty(required=True)

    def get_history(self):
        return HistoryForm(date_time=self.date_time, guess=self.guess, result=self.result)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)
    progress = messages.StringField(6, repeated=True)
    lettersUsed = messages.StringField(7, repeated=True)
    game_canceled = messages.BooleanField(8, required=True)
    attempts_remaining = messages.IntegerField(9, required=True)


class HistoryForm(messages.Message):
    date_time = message_types.DateTimeField(1, required=True)
    guess = messages.StringField(2, required=True)
    result = messages.StringField(3, required=True)


class HistoryForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=False)
    games_played = messages.IntegerField(3, required=False)
    games_won = messages.IntegerField(4, required=False)
    winning_percentage = messages.IntegerField(5, required=False)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class GameForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


class CancelGameForm(messages.Message):
    """Used to cancel game"""
    urlsafe_key = messages.StringField(1, required=True)