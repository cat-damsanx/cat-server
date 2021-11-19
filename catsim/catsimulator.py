import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64

from typing import Tuple
from dataclasses import dataclass
from catsim.cat import generate_item_bank
from catsim.selection import MaxInfoSelector, RandomesqueSelector, MaxInfoGroupWithRandomSelector
from catsim.estimation import HillClimbingEstimator, DifferentialEvolutionEstimator
from catsim.initialization import FixedPointInitializer
from catsim.stopping import MaxItemStopper, MinErrorStopper


df = pd.read_csv(os.environ['QUESTION_DATA_PATH'])

# set level 4.5 to 4 for selector
df.loc[df['level'] == 4.5, 'level'] = 4

# ability bound == question difficult bound
ability_bound = df.level.min(), df.level.max()
print(ability_bound)

# prepare 1PL item bank
item_bank_1PL = generate_item_bank(df.shape[0], itemtype="1PL")
item_bank_1PL[:, 1] = df.level.values

# prepare CAT class
initializer = FixedPointInitializer(ability_bound[0])
selector = MaxInfoGroupWithRandomSelector()
estimator = HillClimbingEstimator(bounds=ability_bound, dodd=False)
# estimator = DifferentialEvolutionEstimator(bounds=ability_bound)
# stopper = MaxItemStopper(max_items=)
stopper = MinErrorStopper(0.58)


def get_question(idx):
    return df.loc[idx, 'code']

@dataclass
class CatSimulator(object):
    """Cat for simulate student response"""

    item_bank: np.ndarray
    initializer: object
    selector: object
    estimator: object
    stopper: object
    user_index: int = 1000
    ability_bound: Tuple[float, float] = (1, 5)

    def first_part(self, question_index: int = None):
        '''
        Hàm này sẽ trả về question code hiện tại mà CAT gợi ý
        '''
        # print("[%s Question number %d %s]" %
        #       ('=' * 10, question_index, '=' * 10))
        if self.isResponse:
            # có response rồi thì mới đưa câu khác
            self.get_question()
        return df.loc[self.question, 'code']
        # self.print_question()

    def third_part(self):
        self.estimate_ability()

        print("[Ability estimated: %f]" % self.theta)

        if self.is_stop():
            print(self.stopper, "satisfied!")
            return True
        return False

    def run(self):
        self.data_initializing()

        for question_index in range(1, 101):
            self.first_part(question_index)

            self.take_response()

            if self.third_part():
                break

    def get_question(self):
        selector_params = dict(
            index=self.user_index,
            items=self.item_bank,
            administered_items=self.administered_items,
            est_theta=self.theta
        )
        self.question = self.selector.select(**selector_params)
        self.administered_items = np.append(
            self.administered_items, self.question)
        self.isResponse = False

    def print_question(self):
        print(df.loc[self.question])

    def estimate_ability(self):
        estimator_params = dict(
            index=self.user_index,
            items=self.item_bank,
            administered_items=self.administered_items,
            response_vector=self.response_pattern,
            est_theta=self.theta
        )
        self.theta = self.estimator.estimate(**estimator_params)
        self.theta_pattern = np.append(self.theta_pattern, self.theta)

    def is_stop(self):
        stopper_params = dict(
            index=self.user_index,
            administered_items=self.item_bank[self.administered_items],
            theta=self.theta
        )
        return self.stopper.stop(**stopper_params)

    def take_response(self, res: int = 0):
        # self.response = [False, True][int(input("Your answer [0/1]: "))]
        self.response = [False, True][res]
        self.response_pattern = np.append(self.response_pattern, self.response)
        self.isResponse = True

    def data_initializing(self):
        self.theta = initializer.initialize()
        self.response_pattern = np.array([], dtype='bool')
        self.theta_pattern = np.array([self.theta], dtype='float')
        self.administered_items = np.array([], dtype='int')
        self.isResponse = True

    def plot(self, figsize: Tuple[float, float] = (12, 6)):
        item_levels = df.loc[self.administered_items, 'level'].values
        fig, ax = plt.subplots(figsize=figsize)
        x = np.arange(self.theta_pattern.shape[0])
        color = np.append('black', np.where(
            self.response_pattern, 'blue', 'red'))
        ax.plot(x[1:], self.theta_pattern[1:], label='Theta Pattern',
                ls='-.', color='orange', alpha=0.75)
        ax.scatter(x[:-1], item_levels, label='Item Level', marker='^')
        ax.scatter(x, self.theta_pattern, color=color)
        ax.set_xticks(x)
        ax.set_xlabel('Time')
        plt.legend(loc='best')
        plt.savefig('cat.png')
        with open('cat.png', 'rb') as f:
            encoded = base64.b64encode(f.read())
            decoded = encoded.decode('utf-8')
            return decoded
        return ''


# cat = CatSimulator(item_bank_1PL, initializer, selector, estimator, stopper)
# cat.run()
# cat.plot()
