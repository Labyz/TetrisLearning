from evolutionary import EA

ea = EA(npop = 50, nrun = 500, ngen = 20, i_rate = 0.90, c_rate = 0.5, m_rate = 0.5, m_size = 0.01, decay_factor = 0.99, pop = [])
ea.run()

# [-0.3429080864695089, 1.01, -1, -0.12005437935753348, -1.01]