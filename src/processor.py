#!/usr/bin/python

import string
import unittest

from instruction import Instruction
from group import Group

class Processor:
    def __init__(self):
        self.instructions = []
        self.groups = []
        self.inputs = []
        self.failures = []
        self.functions = []
        self.name = ''
        self.wordsize = 32

    def AddInstruction(self, instruction):
        self.instructions.append(instruction)

    def FindInstruction(self, instructionName):
        for i in self.instructions:
            if i.name == instructionName:
                return i
        return None

    def FindGroup(self, groupName):
        for g in self.groups:
            if g.name == groupName:
                return g
        return None

    def AddGroup(self, group):
        self.groups.append(group)

    def AddInput(self, i):
        self.inputs.append(i)

    def AddFailure(self, f):
        self.failures.append(f)

    def AddFunction(self, f):
        self.functions.append(f)

    def SetName(self, newName):
        self.name = newName

    def SetWordsize(self, newSize):
        self.wordsize = newSize

    def __repr__(self):
        answer = ''
        print 'Processor', self.name
        print 'Wordsize', self.wordsize
        for i in self.instructions:
            answer += i.__repr__() + '\n'
        for g in self.groups:
            answer += g.__repr__() + '\n'
        answer += 'Input: ' + string.join(self.inputs, ',') + '\n'
        for f in self.failures:
            answer += f.__repr__() + '\n'
        for f in self.functions:
            answer += f.__repr__() + '\n'
        return answer

    def __str__(self):
        return self.__repr__()

class TestProcessor(unittest.TestCase):
    def setUp(self):
        pass

    def test_Instruction(self):
        groupName = 'J'
        g = Group(groupName)
        g.AddInstruction(self.j)

        self.assertIn(self.j, g.instructions)
        self.assertEqual(groupName, g.name)

    def test_MultipleInstructions(self):
        g = Group('R')
        g.AddInstruction(self.add)
        g.AddInstruction(self.sub)

        self.assertIn(self.add, g.instructions)
        self.assertIn(self.sub, g.instructions)

if __name__ == '__main__':
    unittest.main()
