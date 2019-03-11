import pygame
import numpy as np
from tetrisgame import TetrisApp
from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_DOWN
from keras.models import Sequential, model_from_json
from keras.layers import InputLayer, Dense

A = -0.51
B = 0.76
C = -0.36
D = -0.18

class NN_agent():
    def __init__(self, w=10, h=24, eps=0.5, assisted = False):
        self.game = TetrisApp(w, h)
        self.w = w
        self.h = h

        # epsilon-greedy Q learning algorithm inspired by https://adventuresinmachinelearning.com/reinforcement-learning-tutorial-python-keras/
        self.model = Sequential()
        # self.model.add(InputLayer(batch_input_shape=(1,6)))
        self.input_size = self.w + 1
        self.output_size = self.w * 4
        self.model.add(Dense(self.output_size, input_shape=(self.input_size,), activation='relu'))
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])
        self.y = 0.95
        self.eps = eps
        self.decay_factor = 0.9999
        self.keys = [K_LEFT, K_RIGHT, K_DOWN, K_UP]
        self.assisted = assisted

    def start(self, n=100):
        if (n==0):
            while self.game.perdu != True:
                self.run_one_iteration()
        else:
            for i in range(n):
                if i % 100 == 0:
                    print("Episode {} of {}".format(i + 1, n))
                if self.game.perdu == True:
                    self.game.reset()
                self.run_one_iteration()

    def save(self, name):
        model_json = self.model.to_json()
        with open("model_" + name + ".json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("model_" + name + ".h5")
        print("Saved model to disk")

    def load(self, name):
        json_file = open('model_' + name + '.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights("model_" + name + ".h5")
        print("Loaded model from disk")
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])


    def find_best_move(self):
        best_reward = 0
        best_move = 0
        for a in range(self.output_size):
            rotation = a // self.w
            if rotation % 2 == 0:
                tetro = self.game.tetromino
            else:
                tetro = self.game.get_rotated_tetromino()
            margin = np.array(tetro).shape[1]
            x_position = np.minimum(a % self.w, self.w - margin)
            results = self.game.simulate_descent(tetro, x_position)
            reward = A * (results[0]) + B * (results[1]) + C * (results[2]) + D * (results[3]) 
            if a == 0:
                best_reward = reward
                best_move = a
            else:
                if reward > best_reward:
                    best_reward = reward
                    best_move = a
            # print(reward, a)
        # print("best:", best_reward, best_move)
        return(best_move)


    def run_one_iteration(self):
        lines = self.game.lines
        score = self.game.score
        # combo = self.game.combo
        height = self.game.total_height
        column_heights = self.game.column_heights
        bumpiness = self.game.bumpiness
        holes = self.game.holes
        tid = self.game.tetromino_id
        # rid = self.game.rotation_id
        self.eps *= self.decay_factor
        old_input = np.array([np.concatenate((self.game.column_heights, [tid]))])

        # epsilon-greedy exploration
        if np.random.random() < self.eps:
            a = np.random.randint(0, self.output_size)
        else:
            if self.assisted:
                a = self.find_best_move()
            else:
                a = np.argmax(self.model.predict(old_input))
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
        new_input = np.array([np.concatenate((self.game.column_heights, [self.game.tetromino_id]))])

        # reward = A * (self.game.height - height) + B * (self.game.lines - lines) + C * (self.game.holes - holes) + D * (self.game.bumpiness - bumpiness) + self.y * np.max(self.model.predict(new_input))

        reward = A * (self.game.height) + B * (self.game.score/40) + C * (self.game.holes) + D * (self.game.bumpiness) 

        target = reward + self.y * np.max(self.model.predict(new_input))

        # print("---")
        # print(reward)
        # print(target)

        # print("---")
        # print(self.game.height)
        # print(self.game.lines)
        # print(self.game.holes)
        # print(self.game.bumpiness)
        # print(reward)

        target_vec = self.model.predict([old_input])[0]

        target_vec[a] = target

        self.model.fit(old_input, target_vec.reshape(-1, self.output_size), epochs=1, verbose=0)

    def press_key(self, a):
        event = pygame.event.Event(pygame.KEYDOWN, {"key" : self.keys[a]})
        return (event)

player = NN_agent(assisted=True)
name = "nn_assisted_eps0"
player.eps=0
# player.start(1000)
# player.save(name)
while(True):
    player.load(name)
    player.start(1000)
    player.save(name)

