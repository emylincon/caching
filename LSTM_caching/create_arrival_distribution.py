import numpy as np
import pickle

# # write pickle
# ex = {'a':1}
# pickle_out = open('dict.pickle', 'wb')
# pickle.dump (ex, pickle_out)
# pickle_out.close()
#
# # read pickle
# pickle_in = open('dict.pickle','rb')
# example_dict = pickle.load(pickle_in)


for i in range(16):
    pickle_out = open(f'dist/{i}.pickle', 'wb')
    dist = np.random.poisson(1, int(67300/5))
    pickle.dump(dist, pickle_out)
    pickle_out.close()
