import pygame
import numpy as np
from tetrisgame import TetrisApp
from pygame.constants import K_UP, K_LEFT, K_RIGHT, K_DOWN
from keras.models import Sequential
from keras.layers import InputLayer, Dense

class NN_agent():
    def __init__(self):
        self.game = TetrisApp()

        # epsilon-greedy Q learning algorithm inspired by https://adventuresinmachinelearning.com/reinforcement-learning-tutorial-python-keras/
        self.model = Sequential()
        self.model.add(InputLayer(batch_input_shape=(1,2)))
        self.model.add(Dense(4, activation='relu'))
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

    def run_one_iteration(self):
        score = self.game.score
        combo = self.game.combo
        self.eps *= self.decay_factor
        if np.random.random() < self.eps:
            a = np.random.randint(0, 4)
        else:
            a = np.argmax(self.model.predict(np.array([[score, combo]])))
        pygame.event.post(self.press_key(a))
        self.game.run(1)
        target = (self.game.score-score) + self.y * np.max(self.model.predict(np.array([[self.game.score, self.game.combo]])))
        target_vec = self.model.predict(np.array([[score, combo]]))[0]
        target_vec[a] = target
        self.model.fit(np.array([[score, combo]]), target_vec.reshape(-1, 4), epochs=1, verbose=0)

    def press_key(self, a):
        event = pygame.event.Event(pygame.KEYDOWN, {"key" : self.keys[a]})
        return (event)

player = NN_agent()
player.start()

