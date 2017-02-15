#!/usr/bin/python

import unittest

class Instruction:
    def __init__(self, instructionName):
        self.name = instructionName

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Instruction: ' + self.name


class TestInstruction(unittest.TestCase):
    def setUp(self):
        pass

    def test_Instruction(self):
        self.add = Instruction('add')
        self.j = Instruction('j')
        self.sub = Instruction('sub')

        self.assertEqual(str(self.add), 'add')
        self.assertEqual(str(self.j), 'j')
        self.assertEqual(str(self.sub), 'sub')

if __name__ == '__main__':
    unittest.main()
