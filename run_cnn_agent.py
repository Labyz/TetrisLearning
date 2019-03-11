from cnn_agent import CNN_agent

w=10
h=24
lr = 0.8
y = 0.95
eps = 0.8
assist_rate = 0.8
decay_factor = 0.99
A = -0.51
B = 0.76
C = -0.36
D = -0.18
E = -0.1
parameters = [A,B,C,D,E]
silent = False
verbose = True

load_existing_file = False

player = CNN_agent(w = w, h = h, lr = lr, y = y, eps = eps, assist_rate = assist_rate, decay_factor = decay_factor, parameters = parameters, silent = silent, verbose = verbose)

name = "cnn_eps"+str(player.eps)+"_assist"+str(player.assist_rate)+"_decay"+str(player.decay_factor)
if not load_existing_file:
    player.start(1000)
    player.save(name)
while(True):
    player.load(name)
    player.start(1000)
    player.save(name)
    # print(player.eps)