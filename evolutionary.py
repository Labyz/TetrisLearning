from cnn_agent import CNN_agent
import numpy as np
from sklearn.preprocessing import normalize
import pygame

class EA():
    def __init__(self, npop = 100, nrun = 1000, ngen = 100, i_rate = 0.5, c_rate = 0.5, m_rate = 0.5, m_size = 0.01, decay_factor = 0.99, pop = []):
        self.npop = npop
        self.nrun = nrun
        self.ngen = ngen
        self.i_rate = i_rate
        self.c_rate = c_rate
        self.m_rate = m_rate
        self.m_size = m_size
        self.decay_factor = decay_factor
        self.pop = pop
        self.scores = []

    
    def decay_parameters(self):
        self.c_rate *= self.decay_factor
        self.m_rate *= self.decay_factor
        

    def initialization(self):
        for _ in range(self.npop):
            if np.random.random() < self.i_rate:
                param = 2 * np.random.random(5) - 1
            else:
                param = [-1, 1, -1, -1, -1]
            self.pop.append(CNN_agent(eps = 1, assist_rate = 1, decay_factor = 1, parameters = param, silent = True, verbose = False))


    def run_pop(self):
        for i in range(self.npop):
            agent = self.pop[i]
            print("Running agent number", i, " with parameters", agent.parameters)
            agent.start(self.nrun)
            print("Score of agent {}: {}".format(i, agent.max_score))


    def update_score_distribution(self):
        scores = np.array([agent.max_score for agent in self.pop])

        best_index = np.argmax(scores)
        print("Best score:", scores[best_index], "with parameters", self.pop[best_index].parameters)

        scores -= scores.min()
        scores = np.cumsum(normalize([scores], norm = 'l1'))
        self.scores = scores


    def roulette(self):
        ''' roulette-wheel selection '''
        sample = np.random.random()
        index = np.argmax(self.scores > sample)
        return(index)


    def get_child(self, param1, param2):
        new_param = []
        for i in range(len(param1)):
            if np.random.random() < self.c_rate:
                new_param.append(param1[i])
            else:
                new_param.append(param2[i])
        return(new_param)


    def mutate_param(self, param):
        ''' makes param mutate in place '''
        new_param = []
        for i in range(len(param)):
            if np.random.random() < self.m_rate:
                sgn = 2 * np.random.randint(2) - 1
                new_param.append(param[i] + sgn * self.m_size)
            else:
                new_param.append(param[i])
        return(new_param)


    def new_generation(self):
        new_pop = []
        for _ in range(self.npop):
            parent1 = self.pop[self.roulette()]
            parent2 = self.pop[self.roulette()]
            child_param = self.mutate_param(self.get_child(parent1.parameters, parent2.parameters))
            new_pop.append(CNN_agent(eps = 1, assist_rate = 1, decay_factor = 1, parameters = child_param, silent = True, verbose = False))
        self.pop = new_pop
    

    def run(self):
        if len(self.pop) == 0:
            self.initialization()
        for i in range(self.ngen):
            print("Generation", i)
            self.run_pop()
            self.update_score_distribution()
            self.new_generation()
            pygame.event.clear()
