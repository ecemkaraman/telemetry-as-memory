from collections import deque
from river import preprocessing, linear_model, optim, drift


class ClosedLoop:
    def __init__(self, use_trust=True):
        self.model = preprocessing.StandardScaler() | linear_model.LogisticRegression(
            optimizer=optim.SGD(0.05)
        )
        self.det = drift.ADWIN()
        self.use_trust = use_trust
        self.win = deque(maxlen=200)

    def predict_proba(self, x: dict) -> float:
        return self.model.predict_proba_one(x).get(1, 0.1)

    def learn(self, x: dict, y: int, trust: float = 1.0):
        self.model.learn_one(x, y, sample_weight=(trust if self.use_trust else 1.0))

    def update_drift(self, err_rate: float) -> bool:
        return bool(self.det.update(err_rate))
