import pygame
import numpy as np
from tetrisgame import TetrisApp
from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_DOWN
from keras.models import Sequential, model_from_json, Model
from keras.layers import Input, Dense, Conv1D, Conv2D, MaxPooling2D, AveragePooling2D, Reshape, concatenate

A = -0.51
B = 0.76
C = -0.36
D = -0.18
E = -0.1

class CNN_agent():
    def __init__(self, w=10, h=24, lr = 0.8, y = 0.95, eps = 0.5, assist_rate = 0, decay_factor = 0.9999, parameters = [A,B,C,D,E], silent = False, verbose = True):
        self.w = w
        self.h = h
        self.lr = lr
        self.y = y
        self.eps = eps
        self.assist_rate = assist_rate
        self.decay_factor = decay_factor
        self.parameters = parameters
        self.silent = silent
        self.verbose = verbose

        self.output_size = self.w * 4
        self.keys = [K_LEFT, K_RIGHT, K_DOWN, K_UP]
        self.max_score = 0 # used for EA
        self.game = TetrisApp(w, h, silent = self.silent, verbose = self.verbose)

        # epsilon-greedy Q learning algorithm inspired by https://adventuresinmachinelearning.com/reinforcement-learning-tutorial-python-keras/

        main_input = Input(shape=(1, self.h, self.w), name='board')
        aux_input = Input(shape=(1,1), name='tetromino')
        x = Reshape((self.w, self.h, 1))(main_input)
        x = Conv2D(32, 3)(x)
        x = Conv2D(32, 3)(x)
        x = Conv2D(64, 3)(x)
        x = AveragePooling2D(pool_size = (1,18))(x)
        # print(x.shape)
        x = Reshape((4,64))(x)
        # print(x.shape)
        x = Conv1D(128, 3)(x)
        x = Conv1D(128, 1)(x)
        x = Conv1D(128, 2)(x)
        y = concatenate([x, aux_input])
        y = Dense(128, activation = 'relu')(y)
        y = Dense(self.output_size, activation = 'sigmoid')(y)
        self.model = Model(inputs=[main_input, aux_input], outputs = [y])
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])


    def start(self, n=100, reset=False):
        if reset:
            self.game = TetrisApp(self.w, self.h, silent = self.silent, verbose = self.verbose)
            self.max_score = 0
        if (n==0):
            while self.game.perdu != True:
                self.run_one_iteration()
            if self.game.score > self.max_score:
                self.max_score = self.game.score
        else:
            for i in range(n):
                if i % 100 == 0:
                    if self.verbose:
                        print("Episode {} of {}".format(i + 1, n))
                if self.game.perdu == True:
                    if self.game.score > self.max_score:
                        self.max_score = self.game.score
                    self.game = TetrisApp(self.w, self.h, silent = self.silent, verbose = self.verbose)
                self.run_one_iteration()
            if self.game.score > self.max_score:
                self.max_score = self.game.score


    def save(self, name):
        model_json = self.model.to_json()
        with open("model_" + name + ".json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("model_" + name + ".h5")
        if self.verbose:
            print("Saved model to disk")


    def load(self, name):
        json_file = open('model_' + name + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights("model_" + name + ".h5")
        if self.verbose:
            print("Loaded model from disk")
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])


    def find_best_move(self):
        best_reward = 0
        best_move = 0
        # scores = {}
        # for s in range(self.h):
        #     scores[s] = []
        for a in range(self.output_size):
            rotation = a // self.w
            if rotation % 2 == 0:
                tetro = self.game.tetromino
            else:
                tetro = self.game.get_rotated_tetromino()
            margin = np.array(tetro).shape[1]
            x_position = np.minimum(a % self.w, self.w - margin)
            results = self.game.simulate_descent(tetro, x_position)
            # reward = results[1]
            # scores[reward].append(a)
            reward = self.parameters[0] * (results[0] - self.game.total_height) + self.parameters[1] * (results[1] - self.game.lines) + self.parameters[2] * (results[2] - self.game.holes) + self.parameters[3] * (results[3] - self.game.bumpiness) + self.parameters[4] * (results[4] - self.game.max_height)
            if a == 0:
                best_reward = reward
            if reward > best_reward:
                best_reward = reward
                best_move = a
        # index = np.random.randint(0, len(scores[best_reward]))
        # best_move = scores[best_reward][index]
        return(best_move)


    def run_one_iteration(self):
        lines = self.game.lines
        score = self.game.score
        # combo = self.game.combo
        height = self.game.total_height
        column_heights = self.game.column_heights
        board = np.copy(self.game.simple_board())[:self.h, :self.w]
        bumpiness = self.game.bumpiness
        holes = self.game.holes
        tid = self.game.tetromino_id
        # rid = self.game.rotation_id
        self.eps *= self.decay_factor
        old_input = [[[board]], np.array([[[tid]]])]

        # epsilon-greedy exploration
        predicted = False
        if np.random.random() < self.eps:
            if np.random.random() < self.assist_rate: # if random move, assist with probability self.assist_rate
                a = self.find_best_move()
            else:
                a = np.random.randint(0, self.output_size)
        else:
            predicted = True
            weights = self.model.predict(old_input)
            a = np.random.choice(np.flatnonzero(weights == weights.max()))
            # a = np.argmax(weights)
        rotation = a // self.w
        # if rotation % 2 == 0:
        #     margin = np.array(self.game.tetromino).shape[1]
        # else:
        #     margin = np.array(self.game.tetromino).shape[0]
        x_position = a % self.w
        offset = x_position - self.game.x
        # print(x_position)
        # print(offset)

        for _ in range(rotation):
            pygame.event.post(self.press_key(3))
        if offset > 0:
            for _ in range(offset):
                pygame.event.post(self.press_key(1))
        else:
            for _ in range(-offset):
                pygame.event.post(self.press_key(0))

        # this action will make the tetromino go down
        pygame.event.post(self.press_key(2))

        # run one round
        self.game.run(1)

        # Q learning
        new_input = [[[np.copy(self.game.board)[:self.h, :self.w]]], np.array([[[self.game.tetromino_id]]])]

        # reward = A * (self.game.height - height) + B * (self.game.lines - lines) + C * (self.game.holes - holes) + D * (self.game.bumpiness - bumpiness) + self.y * np.max(self.model.predict(new_input))

        reward = ((self.game.score - score)/40) - 0.01
        if reward > 0 and predicted:
            if self.verbose:
                print("!!!")

        target_vec = self.model.predict(old_input)[0][0]

        target = target_vec[a] + self.lr * (reward + self.y * np.max(self.model.predict(new_input) - target_vec[a]))

        # print("---")
        # print(reward)
        # print(target)

        # print("---")
        # print(self.game.height)
        # print(self.game.lines)
        # print(self.game.holes)
        # print(self.game.bumpiness)
        # print(reward)

        target_vec[a] = target

        self.model.fit(old_input, [[[target_vec]]], epochs=1, verbose=0)

    def press_key(self, a):
        event = pygame.event.Event(pygame.KEYDOWN, {"key" : self.keys[a]})
        return (event)