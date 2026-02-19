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

def test_memory():
    mem = RobotMemory()
    assert mem.holding is None
    assert mem.safety_state == "normal"
    assert mem.last_objects == []
    assert mem.last_plan == []
    assert mem.last_command is None

    mem.update_scene([{"name": "bottle"}, {"name": "cup"}])
    assert mem.last_objects == [{"name": "bottle"}, {"name": "cup"}]

    mem.update_plan(["pick bottle", "place on table"], "Pick up the bottle and place it on the table")
    assert mem.last_plan == ["pick bottle", "place on table"]
    assert mem.last_command == "Pick up the bottle and place it on the table"

    mem.stop()
    assert mem.safety_state == "stop"

    mem.reset()
    assert mem.holding is None
    assert mem.safety_state == "normal"
    assert mem.last_objects == []
    assert mem.last_plan == []
    assert mem.last_command is None
