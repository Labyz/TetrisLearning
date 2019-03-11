from cnn_agent import CNN_agent

eps = 0.8
assist_rate = 0.8
decay_factor = 0.99
load_existing_file = False

player = CNN_agent(eps = eps, assist_rate = assist_rate, decay_factor = decay_factor)

name = "cnn_eps"+str(player.eps)+"_assist"+str(player.assist_rate)+"_decay"+str(player.decay_factor)
if not load_existing_file:
    player.start(1000)
    player.save(name)
while(True):
    player.load(name)
    player.start(1000)
    player.save(name)
    # print(player.eps)