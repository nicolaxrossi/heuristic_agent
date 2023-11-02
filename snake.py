from typing import Any
import numpy as np
import random
import copy

###################################################################
# Developed by Nicola Rossi (nicolaxrossi) on 19/10/2023
# last modified: 24/10/2023
###################################################################

def get_x_coord(tuple):
        return tuple[0]
    
def get_y_coord(tuple):
        return tuple[1]

class Board:

    # game field representation
    # O = (0,0)
    # |----------------| y (limit = number of columns -1)
    # |                |
    # |                |
    # |                |
    # |                |
    # |----------------| F = (20, 20)
    # x (limit = number of rows - 1)
    
    # MOVES AND DIRECTIONS
    # right (0, 1)
    # left: (0, -1)
    # up: (-1, 0)
    # down: (1, 0)
    
    moves_direction = {}
    moves_direction['u'] = (-1, 0)
    moves_direction['d'] = (1, 0)
    moves_direction['l'] = (0, -1)
    moves_direction['r'] = (0, 1)

    # list of tuples, containing snake's body parts, head and tail included
    # the element in position 0 is the head, the element in position len(snake_body)-1 is the tail
    #snake = []

    # define the position of the apple, generated randomly
    #apple = None
    
    # score, defined as the number of apples eaten
    #score = 0
    
    # information about the end of game:
    # - the snake has eaten itself
    # - the snake collided with a wall
    # the variable is updated only when the game is finished
    #outcome = ''

    def __init__(self, x_lim, y_lim, snake=None, direction=None, apple=None, score=None, num_moves=None):
        
        # setting snake body
        if snake is None:
            self.snake = [(4,2), (4,1)]
            self.head = self.snake[0]
            self.tail = self.snake[1]
        else:
            self.snake = snake
            self.head = snake[0]
            self.tail = snake[len(snake)-1]
            
        # setting direction
        if direction is None:
            # tuple representing the current snake direction, by default the direction is right ->
            self.snake_direction = (0, 1)
        else:
            self.snake_direction = direction
        
        self.x_limit = x_lim
        self.y_limit = y_lim
        
        # the apple can't be spawned 'on' the snake's body
        if apple is None:
            self.spawn_apple()
        else:
            self.apple = apple

        self.outcome = ''
        if score is None:
            self.score = 0
        else:
            self.score = score

        if num_moves is None:
            self.num_moves = 0
        else:
            self.num_moves = num_moves

    def __eq__(self, other):
        if isinstance(other, Board):
                return self.snake == other.snake and \
                        self.apple == other.apple
                        #self.snake_direction == other.snake_direction and
                        
        else:
            return False

    def __str__(self):
        return self.representation()
    
    def __hash__(self):
        return hash(tuple(self.representation.__dict__.items()))

    def spawn_apple(self):
        self.apple = random.choice(self.spawnable_apple_positions())

    def spawnable_apple_positions(self):

        spawnable_pos = []

        for i in range(0, self.x_limit):
            for j in range(0, self.y_limit):
                t = (i,j)
                if t not in self.snake:
                    spawnable_pos.append(t)

        return spawnable_pos
        
    def copy(self):
        
        x_lim = self.x_limit
        y_lim = self.y_limit
        
        snake = copy.deepcopy(self.snake)
        
        direction = tuple([self.snake_direction[0], self.snake_direction[1]])
        apple = tuple([self.apple[0], self.apple[1]])
        score = self.score
        num_moves = self.num_moves
        
        return self.__class__(x_lim, y_lim, snake, direction, apple, score, num_moves)
        
    def snake_collision(self):
        
        """ function to check if the snake has collided with itself ('has eaten itself') """
        
        # check if the head, after the update, overlaps with some snake's body piece (to be called after update_direction)
        # notice that the list is sliced so that the first element (head) is not considered
        
        if self.head in self.snake[2:]:
            self.outcome = 'eaten itself'
            return True
        else:
            return False
        
    def wall_collision(self):
        
        """ function to check if the snake has collided with a wall """
        
        # as before, after the update, it's checked if the snake's head is over some boundary (collided to some wall)
        
        if self.head[0] >= self.x_limit or self.head[0] < 0:
            self.outcome = 'wall collision'
            return True
        
        if self.head[1] >= self.y_limit or self.head[1] < 0:
            self.outcome = 'wall collision'
            return True
        
        return False
    
    def apply_move(self, move):
        """ funciton to apply the specified move, calling update_direction() function 
        Note: it's ASSUMED the passed move is LEGAL """
        
        new_direction = self.moves_direction[move]
        self.update_direction(new_direction)
        self.num_moves += 1
    
    def update_direction(self, new_direction):
        
        """ function to actually update the snake's head position, with a new direction """
        
        # new_direction specifies the snake is NOW directing up, down, left or right
        self.snake_direction = new_direction
        
        # update head's position in 'snake' list
        self.snake.insert(0, (self.head[0] + self.snake_direction[0], self.head[1] + self.snake_direction[1]))
        
        # update head pointer
        self.head = self.snake[0]
        
        # remove the last piece of snake's body from the list, updating the position of the snake's tail
        self.snake.pop()
        self.tail = self.snake[len(self.snake)-1]
        
        
    def eaten(self):
        
        """ function to check if the snake has eaten the apple """
        
        return self.apple == self.head
    
    def opposite_direction(self, tup):
        
        tup_1 = tup[0]
        tup_2 = tup[1]
        
        tup_1 = -tup_1
        tup_2 = -tup_2
        
        return (tup_1, tup_2)
    
    def grow_snake(self):
        
        """ function to be called when the snake eats an apple, to grow its body by 1 unit """
        
        # the general idea is: append a new tail, at the end of the current snake's body, FOLLOWING the directions
        # of the last two pieces of the current snake's body (ie: the current tail and the previous piece).
        # If this two last pieces share the same value for a coordinate, then the value of the remainin one must be
        # different. So the code below checks which coordinate is 'shared' among this two pieces and sets that
        # coordinate's value in the new tail; then checks whether the remaining coordinate value in the current
        # tail is greater or lower w.r.t. the previous piece, and updates consequently (adding or subtracting 1)
        # the value of this coordinate. The new tuple obtained in such a way is appended at the end of the snake's body,
        # becoming the new tail.
        
        # firstly, the last_element and last_element-1 are get. last_element will become the penultimate element
        # after adding the tail, and last_element-1 will become last_element-2
        #last_element = len(self.snake)-1
        
        #coord_le = self.snake[last_element]
        #coord_le_1 = self.snake[last_element-1]
        
        # to be converted in tuple
        #new_coord = [0,0]
        
        # we use a couple of flags to check which coordinate has the same value in both the tuples
        #coord_1_eq = False
        #coord_2_eq = False
        
        #if coord_le[0] == coord_le_1[0]:
        #    new_coord[0] = coord_le[0]
        #    coord_1_eq = True
        
        #if coord_le[1] == coord_le_1[1]:
        #    new_coord[1] = coord_le[1]
        #    coord_2_eq = True
            
        # then, we check if the remaining coordinate in the last element is lower or higher than the same coordinate
        # in the previous element
        #if coord_1_eq:
        #    if coord_le[1] < coord_le_1[1]:
        #        new_coord[1] = coord_le[1] - 1
                
        #    elif coord_le[1] > coord_le_1[1]:
        #        new_coord[1] = coord_le[1] + 1
        
        #if coord_2_eq:
        #    if coord_le[0] < coord_le_1[0]:
        #        new_coord[0] = coord_le[0] - 1
        #        
        #    elif coord_le[0] > coord_le_1[0]:
        #        new_coord[0] = coord_le[0] + 1
                
        # convert new_coord from list to tuple
        #new_coord = tuple(new_coord)
        
        # append the new tail
        #self.snake.append(new_coord)

        self.snake.insert(0, self.apple)
        
        # update score
        self.score += 1
    
    def legal_moves(self):
        
        """ this functions returns the possibile moves among ('u', 'd', 'l', 'r') checking if the new direction is
        NOT the opposite of the current one, ie: it's not possible to turn back 'directly' """
        
        legal_moves = []
        
        # if the current direction is (-1,0) (up), then it is not possible to move down (1, 0) and viceversa
        # if the current direction is (0,-1) (left), then it is not possible to move right (0, 1) and viceversa
        
        # so, basically, given the current direction the only illegal move is the one such that
        # current direction + new direction = (0,0)
        # For instance, if the snake's moving left (0, -1):
        # - (0,-1)+(1,0) = (1,-1) != (0,0) (down)
        # - (0,-1)+(-1,0) = (-1,-1) != (0,0) (up)
        # - (0,-1)+(0,-1) = (0,-2) (left)
        
        # - (0,-1)+(0,1) = (0,0) (right)
        
        # So we can detect possible moves simply by adding tuple and not returning those with sum equal to 0
        
        dir_1 = self.snake_direction[0]
        dir_2 = self.snake_direction[1]
        
        for move in ['u', 'd', 'l', 'r']:
            tup = self.moves_direction[move]
            tup_1 = tup[0]
            tup_2 = tup[1]
            
            if (dir_1 + tup_1, dir_2 +  tup_2) != (0,0):
                legal_moves.append(move)
            
        return legal_moves

    def representation(self):

        s = []

        for x in range(0,self.x_limit):
            for y in range(0,self.y_limit):

                if y == self.y_limit-1:
                    s.append('.  \n')
                else:
                    s.append('.  ')
        
        # draw apple
        if get_y_coord(self.apple) == self.y_limit-1:
            s[get_x_coord(self.apple)*self.x_limit + get_y_coord(self.apple)] = '@\n'
        else:
            s[get_x_coord(self.apple)*self.x_limit + get_y_coord(self.apple)] = '@  '
        
        # draw body
        for body_part in self.snake:

            if get_x_coord(body_part) < self.x_limit and get_y_coord(body_part) < self.y_limit:
                if get_y_coord(body_part) == self.y_limit-1:
                    s[get_x_coord(body_part)*self.x_limit + get_y_coord(body_part)] = '=\n'
                else:
                    s[get_x_coord(body_part)*self.x_limit + get_y_coord(body_part)] = '=  '
            
        # draw tail
        if get_x_coord(self.snake[len(self.snake)-1]) < self.x_limit and get_y_coord(self.snake[len(self.snake)-1]) < self.y_limit:
            if get_y_coord(self.snake[len(self.snake)-1]) == self.y_limit-1:
                s[get_x_coord(self.snake[len(self.snake)-1])*self.x_limit + get_y_coord(self.snake[len(self.snake)-1])] = '-\n'
            else:
                s[get_x_coord(self.snake[len(self.snake)-1])*self.x_limit + get_y_coord(self.snake[len(self.snake)-1])] = '-  '
        
        # draw head
        if get_x_coord(self.snake[0]) < self.x_limit and get_y_coord(self.snake[0]) < self.y_limit:
            if get_y_coord(self.head) == self.y_limit-1:
                s[get_x_coord(self.head)*self.x_limit + get_y_coord(self.head)] = 'o\n'
            else:
                s[get_x_coord(self.head)*self.x_limit + get_y_coord(self.head)] = 'o  '
                
        return ''.join(s)


# TESTING
def main():
    
    for i in range(0,3):

        print('execution: ', i+1)

        b1 = Board(10, 10)
    
        print(b1)
        print(b1.snake)
        print()

        b2 = b1.copy()

        b1.apply_move('u')
        print(b1)
        print(b1.snake)
        print()

        print(b2)
        print(b2.snake)

        print(b1 == b2)
    
if __name__ == '__main__':
    main()