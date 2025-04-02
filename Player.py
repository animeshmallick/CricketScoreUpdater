class Player:
    def __init__(self, details, isBatsman=True):
        keywords = details.split('$$')
        self.player = 'batsman' if isBatsman else 'bowler'
        if isBatsman:
            self.name = keywords[0]
            self.status = keywords[1]
            self.runs = int(keywords[2])
            self.balls = int(keywords[3])
        else:
            self.name = keywords[0]
            self.overs = float(keywords[1])
            self.runs = int(keywords[3])
            self.wickets = int(keywords[4])
    def to_dict(self):
        if self.player == 'batsman':
            return {"type": self.player, "name": self.name, "status": self.status, "runs": self.runs, "balls": self.balls}
        else:
            return {"type": self.player, "name": self.name, "overs": self.overs, "runs": self.runs, "wickets": self.wickets}