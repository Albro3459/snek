from blessed import Terminal
from blessed.keyboard import Keystroke
from collections import deque
import random
import copy
import time

class GameState:
  def __init__(self):
    self.term = Terminal()
    self.UP = self.term.KEY_UP
    self.RIGHT = self.term.KEY_RIGHT
    self.LEFT = self.term.KEY_LEFT
    self.DOWN = self.term.KEY_DOWN
    self.DIRECTIONS = [ self.LEFT, self.UP, self.RIGHT, self.DOWN ]
    self.MOVEMENT_MAP = { self.LEFT: [0, -1], self.UP: [-1, 0], self.RIGHT: [0, 1], self.DOWN: [1, 0] }
    self.WASD_MAP = { 'w': self.UP, 'a': self.LEFT, 's': self.DOWN, 'd': self.RIGHT, 'W': self.UP, 'A': self.LEFT, 'S': self.DOWN, 'D': self.RIGHT }

    # -------CONFIG--------
    self.BORDER = '⬜️'
    self.BODY = '🟩'
    self.HEAD = '🟥'
    self.SPACE = '　'
    self.APPLE = '🍎'

    # initial snake position
    self.snake = deque([[6, 5], [6, 4], [6, 3]])
    # initial life
    self.dead = False
    # initial food position
    self.food = [5, 10]
    self.h, self.w = 10, 15 # height, width
    # initial score
    self.score = 0
    # initial speed
    self.speed = 3
    # max speed
    self.MAX_SPEED = 6

    # now initialize the world
    self.reset_world()

    # N1 and N2 represents the snake's movement frequency.
    # The snake will only move N1 out of N2 turns.
    self.N1 = 1
    self.N2 = 2

    # M represents how often the snake will grow.
    # The snake will grow every M turns.
    self.M = 9

    self.val = Keystroke()
    self.turn = 0
    # -----CONFIG END------

    self.messages = ["you can do it!", "dont get eaten!", "run, forest, run!", "where theres a will, theres a way", "you can beat it!", "outsmart the snake!"]
    self.message = None

  def reset_world(self):
    self.world = [[self.SPACE] * self.w for _ in range(self.h)]
    for i in range(self.h):
      self.world[i][0] = self.BORDER
      self.world[i][-1] = self.BORDER
    for j in range(self.w):
      self.world[0][j] = self.BORDER
      self.world[-1][j] = self.BORDER
    for s in self.snake:
      self.world[s[0]][s[1]] = self.BODY
    head = self.snake[0]
    self.world[head[0]][head[1]] = self.HEAD
    self.world[self.food[0]][self.food[1]] = self.APPLE

def main():
  state = GameState()

  with state.term.cbreak(), state.term.hidden_cursor():
    # clear the screen
    print(state.term.home + state.term.clear)
    
    # initialize the world
    for row in state.world:
      print(''.join(row))

    # instructions
    print('use arrow keys or WASD to move!')
    print("this time, youre the food 😱\n")
    print('I recommend expanding the terminal window')
    print('so the game has enough space to run')

    while True:
      # check for restart
      if state.dead:
        state.val = Keystroke()
        print('you were eaten by snek! :(' + state.term.clear_eos)
        print('use arrow keys or WASD to try again!' + state.term.clear_eos)
        time.sleep(1) # wait 1 second before checking in case the player is holding a key
        state.val = state.term.inkey(timeout=5) # check for next key for 5 seconds
        if state.val.code in state.DIRECTIONS or state.val in state.WASD_MAP.keys():
          state = GameState() # reset
        else:
          break

      # Get key press
      state.val = state.term.inkey(timeout=1/state.speed)

      # let the snake decide where to move
      state.head = state.snake[0]
      y_diff = state.food[0] - state.head[0]
      x_diff = state.food[1] - state.head[1]

      preferred_moves = []
      if abs(y_diff) > abs(x_diff):
        if y_diff <= 0:
          preferred_moves.append(state.UP)
        else:
          preferred_moves.append(state.DOWN)
      else:
        if x_diff >= 0:
          preferred_moves.append(state.RIGHT)
        else:
          preferred_moves.append(state.LEFT)

      preferred_moves += list(state.DIRECTIONS) # Add extra moves just in case
      
      next_move = None
      for move in preferred_moves:
        movement = state.MOVEMENT_MAP[move]
        state.head_copy = copy.copy(state.head)
        state.head_copy[0] += movement[0]
        state.head_copy[1] += movement[1]
        state.heading = state.world[state.head_copy[0]][state.head_copy[1]]
        if state.heading == state.BORDER:
          continue
        elif state.heading == state.BODY:
          # For every M  turns, the snake grows
          # longer. So, the head can move to the
          # tail's location only if turn % M  != 0
          if state.head_copy == state.snake[-1] and state.turn % state.M  != 0:
            next_move = state.head_copy
            break
        else:
          next_move = state.head_copy
          break
      
      if next_move is None:
        break
      
      state.turn += 1
      # snake only moves N - 1 out of N turns.
      # before the snake moves, clear the current
      # location of the food.
      state.world[state.food[0]][state.food[1]] = state.SPACE
      if state.turn % state.N2 < state.N1:
        state.snake.appendleft(next_move)
        # for every M turns or so, the snake grows longer and everything becomes faster
        state.world[state.head[0]][state.head[1]] = state.BODY
        if state.turn % state.M  != 0:
          state.speed = min(state.speed * 1.05, state.MAX_SPEED)
          tail = state.snake.pop()
          state.world[tail[0]][tail[1]] = state.SPACE
        state.world[next_move[0]][next_move[1]] = state.HEAD

      # And then the food moves
      food_copy = copy.copy(state.food)
      # First, encode the movement in food_copy
      if state.val.code in state.DIRECTIONS or state.val in state.WASD_MAP.keys():
        direction = None
        if state.val in state.WASD_MAP.keys():
          direction = state.WASD_MAP[state.val]
        else:
          direction = state.val.code
        movement = state.MOVEMENT_MAP[direction]
        food_copy[0] += movement[0]
        food_copy[1] += movement[1]

      # Check where the food is heading
      food_heading = state.world[food_copy[0]][food_copy[1]]
      # You only die if the snake's head eats you. The body won't do any damage.
      if food_heading == state.HEAD:
        state.dead = True
      # Only move the food if you're trying to
      # move to an empty state.space.
      if food_heading == state.SPACE:
        state.food = food_copy
      # If somehow the food's current location
      # overlaps with the snake's body, then
      # the apple's dead.
      if state.world[state.food[0]][state.food[1]] == state.BODY or state.world[state.food[0]][state.food[1]] == state.HEAD:
        state.dead = True
      if not state.dead:
        state.world[state.food[0]][state.food[1]] = state.APPLE

      print(state.term.move_yx(0, 0))
      for row in state.world:
        print(''.join(row))
      state.score = len(state.snake) - 3
      print(f'score: {state.turn} - size: {len(state.snake)}' + state.term.clear_eol)
      if state.turn % 50 == 0:
        state.message = random.choice(state.messages)
      if state.message:
        print(state.message + state.term.clear_eos)
      print(state.term.clear_eos, end='')

  if not state.dead:
    print('woah you woncd Snek how did you do it?!' + state.term.clear_eos)

main()