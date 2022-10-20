class Division:
    def __init__(self, name):
        self.name = name
        self.soldiers = []
        self.policy = None

    def add_soldier(self, soldier):
        if soldier not in self.soldiers:
            self.soldiers.append(soldier)

    def remove_soldier(self, soldier):
        if soldier in self.soldiers:
            self.soldiers.remove(soldier)