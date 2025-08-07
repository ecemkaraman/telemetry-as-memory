from river import linear_model, preprocessing, compose, metrics
from river.utils import dict2numpy
import pandas as pd


class OnlineModel:
    def __init__(self, target="latency"):
        # Store the target variable name (e.g., 'latency', 'cpu', 'errors')
        self.target = target

        # Define pipeline: Normalize inputs → Linear regression
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(), linear_model.LinearRegression()
        )

        # For monitoring performance
        self.metric = metrics.MAE()

    def partial_fit(self, x: dict):
        """
        Fit the model on one observation at a time.
        Expects a dictionary with the target included.
        """
        y = x.pop(self.target)
        self.model.learn_one(x, y)
        self.metric = self.metric.update(y_true=y, y_pred=self.model.predict_one(x))

    def predict(self, x: dict):
        return self.model.predict_one(x)

    def score(self):
        return self.metric.get()

    def reset(self):
        self.model = compose.Pipeline(
            preprocessing.StandardScaler(), linear_model.LinearRegression()
        )
        self.metric = metrics.MAE()
