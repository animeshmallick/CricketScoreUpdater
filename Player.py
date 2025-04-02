class Player:
    def __init__(self, details):
        keywords = details.split('$$')
        self.name = keywords[0]
        self.status = keywords[1]
        self.runs = int(keywords[2])
        self.balls = int(keywords[3])
    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "runs": self.runs,
            "balls": self.balls
        }