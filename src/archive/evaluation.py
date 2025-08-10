"""Track Recovery, FPR, Drift Detections"""


class Evaluator:
    def __init__(self):
        self.drift_detected = 0
        self.false_positives = 0
        self.total = 0

    def log(self, predicted, actual):
        if predicted != actual:
            self.false_positives += 1
        self.total += 1

    def report(self):
        fpr = self.false_positives / self.total
        print(f"False Positive Rate: {fpr:.2f}")
