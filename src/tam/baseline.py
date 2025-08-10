# src/tam/baseline.py
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression


class StaticBaseline:
    def __init__(self, retrain_every=300, min_samples=50):
        self.vec = DictVectorizer(sparse=False)
        self.X_buf, self.y_buf = [], []
        self.m = LogisticRegression(max_iter=200)
        self.ticks = 0
        self.retrain_every = retrain_every
        self.min_samples = min_samples
        self.fitted = False

    def _can_retrain(self):
        if len(self.y_buf) < self.min_samples:
            return False
        # need at least 2 classes present
        return len(set(self.y_buf)) >= 2

    def step(self, x: dict, y: int) -> float:
        self.ticks += 1
        self.X_buf.append(x)
        self.y_buf.append(y)

        if (self.ticks % self.retrain_every) == 0 and self._can_retrain():
            X = self.vec.fit_transform(self.X_buf)
            self.m.fit(X, self.y_buf)
            self.fitted = True

        if self.fitted:
            Xq = self.vec.transform([x])
            return float(self.m.predict_proba(Xq)[0][1])
        # not fitted yet → safe default
        return 0.1
