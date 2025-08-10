from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression


class StaticBaseline:
    def __init__(self, retrain_every=300):
        self.vec = DictVectorizer(sparse=False)
        self.X_buf, self.y_buf = [], []
        self.m = LogisticRegression(max_iter=200)
        self.ticks = 0
        self.retrain_every = retrain_every
        self.fitted = False

    def step(self, x: dict, y: int) -> float:
        self.ticks += 1
        self.X_buf.append(x)
        self.y_buf.append(y)
        if (self.ticks % self.retrain_every) == 0:
            X = self.vec.fit_transform(self.X_buf)
            self.m.fit(X, self.y_buf)
            self.fitted = True
        if self.fitted:
            Xq = self.vec.transform([x])
            return float(self.m.predict_proba(Xq)[0][1])
        return 0.1
