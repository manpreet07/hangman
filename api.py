# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import sys

import endpoints
from google.appengine.api import memcache
from google.appengine.api import taskqueue
from protorpc import remote, messages
import re
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm, ScoreForms, GameForms, HistoryForms

from models import User, Game, Score, History
from utils import get_by_urlsafe

sys.path.insert(0, 'libs')

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1), )
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MakeMoveForm, urlsafe_game_key=messages.StringField(1), )
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1), email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'


@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
            request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key)
        except ValueError:
            raise endpoints.BadRequestException('Error while creating new game')

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        if game.game_canceled:
            return game.to_form('Game is already canceled!')

        target_list = list(game.target)

        if game.attempts_remaining < 1:
            game.post_transaction(request.guess, "Your do not have any remaining")
            game.end_game(True)
            return game.to_form('You loose!')

        if re.search('[a-zA-Z]', request.guess):
            if len(request.guess) > 1:
                if request.guess == game.target:
                    game.post_transaction(request.guess, "Your guess is correct!")
                    game.end_game(True)
                    return game.to_form('You win!')
                else:
                    game.post_transaction(request.guess, "Your guess is incorrect!")
                    game.end_game(False)
                    return game.to_form('You loose!')
            if request.guess not in game.progress:
                if request.guess in target_list and request.guess not in game.letters_used:
                    for key, val in enumerate(target_list):
                        if val == request.guess:
                            game.progress[key] = request.guess
                    if game.progress != target_list:
                        game.post_transaction(request.guess, "Your guess is correct!")
                        game.put()
                        return game.to_form('Your guess is correct!')
                    else:
                        game.end_game(True)
                        return game.to_form('You win!')
                elif request.guess not in target_list and request.guess not in game.letters_used:
                    game.attempts_remaining -= 1
                    if "_" in game.letters_used:
                        _index = game.letters_used.index("_")
                        game.letters_used[_index] = request.guess
                    if game.attempts_remaining > 0:
                        game.post_transaction(request.guess, "Your guess is not correct!")
                        game.put()
                        return game.to_form('Your guess is not correct!')
                    else:
                        game.post_transaction(request.guess, "Your do not have any remaining")
                        game.end_game(True)
                        return game.to_form('You loose!')
            else:
                return game.to_form('Already used!')
        else:
            return game.to_form('Please enter only alphabets!')

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        scores = Score.query()
        return ScoreForms(items=[score.get_score() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.get_score() for score in scores])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='games/{urlsafe_game_key}/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_average_attempts_remaining(self, request):
        """Get the cached average moves remaining"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.game_status("Game already over")
        if game.game_canceled:
            return game.game_status("Game already cancelled")
        else:
            return game.game_status("Game is in progress")

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='scores/user/{user_name}/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """User Games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                'A User with that name does not exist!')
        games = Game.query(Game.user == user.key, Game.game_canceled == False, Game.game_over == False)
        return GameForms(items=[game.to_form('All Games') for game in games])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='games/{urlsafe_game_key}/cancel_game',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel Game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.game_status("Game already over")
        else:
            game.cancel_the_game()
            return game.game_status("Game Canceled")

    @endpoints.method(response_message=ScoreForms,
                      path='scores/high_scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """High scores"""
        scores = Score.query().order(-Score.games_won)
        return ScoreForms(items=[score.get_score() for score in scores])

    @endpoints.method(response_message=ScoreForms,
                      path='scores/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """User Rankings"""
        scores = Score.query().order(-Score.winning_percentage)
        return ScoreForms(items=[score.get_ranking() for score in scores])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForms,
                      path='games/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Game History"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        history = History.query(History.game == game.key).order(-History.date_time)
        return HistoryForms(items=[transaction.get_history() for transaction in history])

    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of Games"""
        games = Game.query(Game.game_over == False, Game.game_canceled == False).fetch()
        if games:
            count = len(games)
            total_attempts_remaining = sum([game.attempts_remaining
                                            for game in games])
            average = float(total_attempts_remaining) / count
            memcache.set(MEMCACHE_MOVES_REMAINING,
                         'The average moves remaining is {:.2f}'.format(average))


api = endpoints.api_server([HangmanApi])
