class RobotMemory:
    def __init__(self):
        self.holding = None
        self.safety_state = "normal"

    def snapshot(self):
        return {
            "holding": self.holding,
            "safety_state": self.safety_state
        }

    def stop(self):
        self.safety_state = "stop"

    def reset(self):
        self.holding = None
        self.safety_state = "normal"