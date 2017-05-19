import string
import processor

class Function:
    def __init__(self, functionName):
        self.name = functionName
        self.parameters = []

    def AddParameter(self, parameter):
        self.parameters.append(parameter)

    def GenerateCode(self, targetRegister):
        return self.name + '(' + targetRegister + string.join(map(str, self.parameters), ',') + ')\n'

    def __str__(self):
        return self.name + '(' + string.join(map(str, self.parameters), ',') + ')'

    def __repr__(self):
        return 'Function: ' + self.name + '(' + string.join(map(str, self.parameters), ',') + ')'


class BitFlip(Function):
    def __init__(self):
        Function.__init__(self, 'BitFlip')

    def GenerateCode(self, targetRegister):
        if self.parameters[0] == 'random':
            p = processor.Processor()
            randomRange = p.wordsize
            return 'bitFlip(%s, randomRange(%s))' % (targetRegister, randomRange)
        else:
            return 'bitFlip(%s, %s)' % (targetRegister, self.parameters[0])


class StuckAt(Function):
    def __init__(self):
        Function.__init__(self, 'StuckAt')

    def GenerateCode(self, targetRegister):
        if self.parameters[0] == 'random':
            p = processor.Processor()
            randomRange = p.wordsize
            print randomRange
            return 'stuckAt(%s, randomRange(%s), %s)' % (targetRegister, randomRange, self.parameters[1])
        else:
            return 'stuckAt(%s, %s, %s)' % (targetRegister, self.parameters[0], self.parameters[1])
