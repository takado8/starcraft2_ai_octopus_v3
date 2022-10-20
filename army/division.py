class Division:
    def __init__(self, name, micro):
        self.name = name
        self.soldiers = []
        self.policy = None
        self.micro = micro

    def add_soldier(self, soldier):
        if soldier not in self.soldiers:
            self.soldiers.append(soldier)

    def remove_soldier(self, soldier):
        if soldier in self.soldiers:
            self.soldiers.remove(soldier)