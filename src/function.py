import string


class Function:
    def __init__(self, functionName):
        self.name = functionName
        self.parameters = []

    def AddParameter(self, parameter):
        self.parameters.append(parameter)

    def __str__(self):
        return self.name + '(' + string.join(map(str, self.parameters), ',') + ')'

    def __repr__(self):
        return 'Function: ' + self.name + '(' + string.join(map(str, self.parameters), ',') + ')'