class RobotMemory:
    def __init__(self):
        self.holding = None
        self.safety_state = "normal"
        self.last_objects = []
        self.last_plan = []
        self.last_command = None

    def snapshot(self):
        return {
            "holding": self.holding,
            "safety_state": self.safety_state,
            "last_objects": self.last_objects,
            "last_plan": self.last_plan,
            "last_command": self.last_command
        }

    def update_scene(self, objects):
        self.last_objects = objects

    def update_plan(self, plan, cmd):
        self.last_plan = plan
        self.last_command = cmd

    def stop(self):
        self.safety_state = "stop"

    def reset(self):
        self.holding = None
        self.safety_state = "normal"
        self.last_objects = []
        self.last_plan = []
        self.last_command = None
