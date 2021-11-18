import numpy as np
from catsim.cat import generate_item_bank
from catsim.initialization import RandomInitializer
from catsim.selection import MaxInfoSelector
from catsim.estimation import NumericalSearchEstimator
from catsim.stopping import MaxItemStopper
from catsim.simulation import Simulator

it_1PL = np.array([1, 2, 3, 3, 3, 3, 2, 2, 1, 1])

initializer = RandomInitializer(dist_params=(1, 4))
selector = MaxInfoSelector()
estimator = NumericalSearchEstimator()
stopper = MaxItemStopper(20)