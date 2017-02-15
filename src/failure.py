class Failure:
    def __init__(self, instr_group, function, probability):
        self.instr_group = instr_group
        self.function = function
        self.probability = probability

    def __repr__(self):
        return 'Failure: ' + self.instr_group + ' has ' + str(self.function) + ' with probability ' + self.probability