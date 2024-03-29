import numpy as np
from scipy import stats
from catsim import irt
from catsim.simulation import Stopper


class MaxItemStopper(Stopper):
    """Stopping criterion for maximum number of items in a test

    :param max_items: the maximum number of items in the test"""

    def __str__(self):
        return 'Maximum Item Number Initializer'

    def __init__(self, max_items: int):
        super(MaxItemStopper, self).__init__()
        self._max_items = max_items

    def stop(self,
        index: int = None,
        items: np.ndarray = None,
        administered_items: list = None,
        **kwargs
    ) -> bool:
        """Checks whether the test reached its stopping criterion for the given user

        :param index: the index of the current examinee
        :param index: the index of the current examinee
        :param administered_items: a list containing the indexes of items that were already administered
        :returns: `True` if the test met its stopping criterion, else `False`"""

        if (index is None or self.simulator is None) and administered_items is None:
            raise ValueError

        if administered_items is None:
            administered_items = self.simulator.items[self.simulator.administered_items[index]]
        else:
            administered_items = items[administered_items]

        n_items = administered_items.shape[0]
        if n_items > self._max_items:
            raise ValueError(
                'More items than permitted were administered: {0} > {1}'.format(
                    n_items, self._max_items
                )
            )

        return n_items == self._max_items


class MinErrorStopper(Stopper):
    """Stopping criterion for minimum standard error of estimation (see :py:func:`catsim.irt.see`)

    :param min_error: the minimum standard error of estimation the test must achieve before stopping"""

    def __str__(self):
        return 'Minimum Error Initializer'

    def __init__(self, min_error: float):
        super(MinErrorStopper, self).__init__()
        self._min_error = min_error

    def stop(
        self,
        index: int = None,
        items: np.ndarray = None,
        administered_items: list = None,
        theta: float = None,
        **kwargs
    ) -> bool:
        """Checks whether the test reached its stopping criterion

        :param index: the index of the current examinee
        :param administered_items: a list containing the indexes of items that were already administered
        :param theta: a float containing the a proficiency value to which the error will be calculated
        :returns: `True` if the test met its stopping criterion, else `False`"""

        if (index is None or
            self.simulator is None) and (administered_items is None or theta is None):
            raise ValueError

        if administered_items is None and theta is None:
            theta = self.simulator.latest_estimations[index]
            administered_items = self.simulator.items[self.simulator.administered_items[index]]
        else:
            administered_items = items[administered_items]

        if theta is None:
            return False

        self.see = irt.see(theta, administered_items)
        print("Current error: %f" % self.see)
        return self.see < self._min_error

class MinConfidenceStopper(Stopper):
    """Stopping criterion for minimum confidence that theta exceeds a threshold

    :param min_confidence: the minimum confidence that the user exceeds the threshold the test must achieve before stopping
    :param theta_threshold: value of theta that needs to be exceeded with a particular confidence level before stopping"""

    def __str__(self):
        return 'Minimum Confidence Initializer'

    def __init__(self, min_confidence: float, theta_threshold: float = 1.):
        super(MinConfidenceStopper, self).__init__()
        self._min_confidence = min_confidence
        self._theta_threshold = theta_threshold

    def stop(
        self,
        index: int = None,
        items: np.ndarray = None,
        administered_items: list = None,
        theta: float = None,
        **kwargs
    ) -> bool:
        """Checks whether the test reached its stopping criterion

        :param index: the index of the current examinee
        :param items: a matrix containing item parameters in the format that `catsim` understands
                      (see: :py:func:`catsim.cat.generate_item_bank`)
        :param administered_items: a list containing the indexes of items that were already administered
        :param theta: a float containing the a proficiency value to which the error will be calculated
        :returns: `True` if the test met its stopping criterion, else `False`"""

        if (index is None or
            self.simulator is None) and (administered_items is None or theta is None):
            raise ValueError

        if administered_items is None and theta is None:
            theta = self.simulator.latest_estimations[index]
            administered_items = self.simulator.items[self.simulator.administered_items[index]]
        else:
            administered_items = items[administered_items]

        if theta is None:
            return False

        crnt_se = irt.see(theta, administered_items)
        crnt_confidence = 1 - stats.norm.cdf(self._theta_threshold, loc = theta, scale = crnt_se)
        return crnt_confidence > self._min_confidence
