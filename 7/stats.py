class Stats:
    def __init__(self) -> None:
        self.rtt_min = 1e9
        self.rtt_max = 0
        self.rtt_sum = 0
        self.total_count = 0
        self.recieved = 0

    def add_recived(self, rtt: float):
        self.total_count += 1
        self.recieved += 1
        self.rtt_sum += rtt

        self.rtt_max = max(rtt, self.rtt_max)
        self.rtt_min = min(rtt, self.rtt_min)

    def add_missed(self):
        self.total_count += 1

    def stats(self):
        return self.rtt_min, self.rtt_max, self.rtt_sum / max(1, self.total_count), 1 - self.recieved / max(1, self.total_count)