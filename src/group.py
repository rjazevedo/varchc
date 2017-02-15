#!/usr/bin/python

import string
import unittest
from instruction import Instruction


class Group:
    def __init__(self, groupName):
        self.name = groupName
        self.instructions = []

    def AddInstruction(self, instruction):
        self.instructions.append(instruction)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Group: ' + self.name + ': ' + string.join(map(str, self.instructions), ',')

class TestGroup(unittest.TestCase):
    def setUp(self):
        self.add = Instruction('add')
        self.j = Instruction('j')
        self.sub = Instruction('sub')

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
