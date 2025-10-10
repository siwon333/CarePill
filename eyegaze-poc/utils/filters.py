class EMA:
    def __init__(self, alpha=0.5, v0=None):
        self.alpha = alpha
        self.v = v0
    def update(self, x):
        self.v = x if self.v is None else self.alpha*x + (1-self.alpha)*self.v
        return self.v
