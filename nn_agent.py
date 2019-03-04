import pygame
import numpy as np
from tetrisgame import TetrisApp
from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_DOWN
from keras.models import Sequential, model_from_json
from keras.layers import InputLayer, Dense

a = -0.51
b = 0.019
c = -0.36
d = -0.18

class NN_agent():
    def __init__(self, w=10, h=24):
        self.game = TetrisApp(w, h)

        # epsilon-greedy Q learning algorithm inspired by https://adventuresinmachinelearning.com/reinforcement-learning-tutorial-python-keras/
        self.model = Sequential()
        # self.model.add(InputLayer(batch_input_shape=(1,6)))
        self.model.add(Dense(4, input_shape=(6,), activation='relu'))
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])
        self.y = 0.95
        self.eps = 0.5
        self.decay_factor = 0.9999
        self.keys = [K_LEFT, K_RIGHT, K_DOWN, K_UP]

    def start(self, n=10000):
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

    def save(self):
        model_json = self.model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("model.h5")
        print("Saved model to disk")

    def load(self):
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        self.model = model_from_json(loaded_model_json)
        # load weights into new model
        self.model.load_weights("model.h5")
        print("Loaded model from disk")
        self.model.compile(loss='mse', optimizer='adam', metrics=['mae'])

    def run_one_iteration(self):
        score = self.game.score
        # combo = self.game.combo
        height = self.game.total_height
        bumpiness = self.game.bumpiness
        holes = self.game.holes
        tid = self.game.tetromino_id
        rid = self.game.rotation_id
        self.eps *= self.decay_factor

        # epsilon-greedy exploration
        if np.random.random() < self.eps:
            a = np.random.randint(0, 4)
        else:
            a = np.argmax(self.model.predict(np.array([[height, score, holes, bumpiness, tid, rid]])))
        pygame.event.post(self.press_key(a))
        
        # to speed up the process
        for _ in range(5):
            pygame.event.post(self.press_key(3))

        # run one round
        self.game.run(1)

        # Q learning
        target = a * (self.game.height - height) + b * (self.game.score - score) + c * (self.game.holes - holes) + d * (self.game.bumpiness - bumpiness) + self.y * np.max(self.model.predict(np.array([[self.game.height, self.game.score, self.game.holes, self.game.bumpiness, self.game.tetromino_id, self.game.rotation_id]])))
        target_vec = self.model.predict(np.array([[height, score, holes, bumpiness, tid, rid]]))[0]
        target_vec[a] = target
        self.model.fit(np.array([[height, score, holes, bumpiness, tid, rid]]), target_vec.reshape(-1, 4), epochs=1, verbose=0)

    def press_key(self, a):
        event = pygame.event.Event(pygame.KEYDOWN, {"key" : self.keys[a]})
        return (event)

player = NN_agent(8, 10)
player.load()
player.start(1000)
player.save()

