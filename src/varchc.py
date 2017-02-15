#!/usr/bin/python

import argparse
import sys
import unittest

import pyparsing as pp

from failure import Failure
from function import Function
from group import Group
from instruction import Instruction
from processor import Processor


class ParserActions:
    def __init__(self, proc = None):
        self.processor = proc
        return

    def SetProcessor(self, proc):
        self.processor = proc

    def VArchCError(self, message, str, loc):
        print 'ERROR: line %d, col %d: %s' % (pp.lineno(loc, str), pp.col(loc, str), message)

    def ImportFile(self, str, loc, tokens):
        fileName = tokens[0] + '.vac'
        print 'importing', fileName
        p = VArchCParser(self.processor)
        p.ParseFile(fileName)

    def AddInstructions(self, str, loc, tokens):
        for tok in tokens:
            self.processor.AddInstruction(Instruction(tok))

    def AddGroup(self, str, loc, tokens):
        group = Group(tokens[0])
        for instr in tokens[1:]:
            instruction = self.processor.FindInstruction(instr)
            if (instruction != None):
                group.AddInstruction(instruction)
            else:
                self.VArchCError('Invalid instruction', str, loc)
        self.processor.AddGroup(group)

    def AddInput(self, str, loc, tokens):
        self.processor.AddInput(tokens[0])

    def AddFunction(self, str, loc, tokens):
        function = Function(tokens[0])
        for parameter in tokens[1:]:
            function.AddParameter(parameter)
        self.processor.AddFunction(function)
        return function

    def AddFailure(self, str, loc, tokens):
        failure = Failure(tokens[0], tokens[1], tokens[2])
        self.processor.AddFailure(failure)


class VArchCParser:
    content = []

    processor = None
    actions = ParserActions(processor)

    __colon = pp.Literal(':')
    __lPar = pp.Literal('(')
    __rPar = pp.Literal(')')
    __lBrace = pp.Literal('{')
    __rBrace = pp.Literal('}')
    __lBrack = pp.Literal('[')
    __rBrack = pp.Literal(']')
    __semiColon = pp.Literal(';').suppress()
    __comma = pp.Literal(',')
    __equal = pp.Literal('=')
    __quotes = pp.Literal('"')
    __percent = pp.Literal('%')
    __lThan = pp.Literal('<')
    __gThan = pp.Literal('>')
    __dot = pp.Literal('.')
    __plus = pp.Literal('+')
    __or = pp.Literal('|')

    __comment1 = pp.Literal('//').suppress() + pp.restOfLine.suppress()
    __comment2 = pp.Literal('/*').suppress() + pp.SkipTo(pp.Literal('*/'), include = True)
    __comment3 = pp.Literal('#').suppress() + pp.restOfLine.suppress()

    __comments = __comment1 | __comment2 | __comment3

    __unit = ['K', 'M', 'G', 'T']
    # ID = [a-zA-Z][_a-zA-Z0-9]*
    __symbol = pp.Word(pp.alphas, pp.alphanums + '_').setName('symbol')
    __str = __quotes + pp.SkipTo(__quotes, include=True)

    # INT = [0-9]+
    __int = pp.Word(pp.nums)

    # HEX = (0x | 0X) [0-9a-fA-F]+
    __hexnumber = (pp.Literal('0x').suppress() | pp.Literal('0X').suppress()) + pp.Word(pp.nums + 'abcdefABCDEF')
    __hexnumber.setName('hexadecimal number')

    # NUM = ([0-9]+ | HEX)
    __number = (__int ^ __hexnumber).setName('number')

    # FP_Num
    __fpNum = pp.Combine(pp.Word(pp.nums) + pp.Optional(__dot + pp.Word(pp.nums)))

    # SIZE = NUM + (K | M | G | T | k | m | g | t)
    __size = (__number + pp.oneOf(__unit, caseless=True) * (0, 1)).setName('size')

    # FILENAME = "[any char]"
    __filename = __symbol.setName('filename')

    __parameter = __symbol | __fpNum | __number

    __function = __symbol + __lPar.suppress() + pp.ZeroOrMore(__parameter + pp.Optional(__comma).suppress()) + __rPar.suppress()
    __function.setParseAction(actions.AddFunction)

    __inputClause = pp.Literal('input').suppress() + __symbol + __semiColon
    __inputClause.setParseAction(actions.AddInput)

    __importClause = pp.Literal('import').suppress() + __filename + __semiColon
    __importClause.setParseAction(actions.ImportFile)

    __instructionClause = pp.Literal('instruction').suppress() + pp.OneOrMore(__symbol + pp.Optional(__comma).suppress()) + __semiColon
    __instructionClause.setParseAction(actions.AddInstructions)

    __groupClause = pp.Literal('group').suppress() + __symbol + __lBrace.suppress() + \
                    pp.OneOrMore(__symbol + pp.Optional(__comma).suppress()) + __rBrace.suppress() +  __semiColon
    __groupClause.setParseAction(actions.AddGroup)

    __failureClause = __symbol + pp.Literal('has').suppress() + __function + \
                      pp.Literal('with').suppress() + pp.Literal('probability').suppress() + \
                      __parameter + __semiColon
    __failureClause.setParseAction(actions.AddFailure)

    __varchc_token = __importClause | __instructionClause | __groupClause | __inputClause | __failureClause | __function

    __varchc_tokens = pp.ZeroOrMore(__varchc_token)
    __varchc_tokens.ignore(__comments)
    __varchc_tokens.setFailAction(actions.VArchCError)

    def __init__(self, processor = None):
        if (processor == None):
            self.processor = Processor()
        else:
            self.processor = processor

        self.actions.SetProcessor(self.processor)

    def ParseFile(self, fileName):
        print 'parsing file', fileName
        self.content.extend(self.__varchc_tokens.parseFile(fileName, parseAll=True))

    def ClearParser(self):
        self.processor = Processor()
        self.content = []
        self.actions = ParserActions()


class TestVarchC(unittest.TestCase):
    def setUp(self):
        pass

    def test_processor(self):
        p = Processor()
        i = Instruction('add')
        p.AddInstruction(i)
        g = Group('R')
        g.AddInstruction(i)
        p.AddGroup(g)
        self.assertEqual(p.FindInstruction('add'), i)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='VArchC: Generate Variation Aware ArchC Post-Behavior Models')
#    parser.add_argument('-d', '--dblp', action='store_true', help='Fetch DBLP Canonical name')
    parser.add_argument('-i', '--input', type=str, help='Define input parameter (eg: -i p=5)')
    parser.add_argument('-t', '--test', action='store_true', help='Test parser and infrastructure')
#    parser.add_argument('-s', '--sleep', type=int, help='Sleep time in seconds between web queries (default: 20)')
    parser.add_argument('source', type=str, help='Source VArchC file (.vac)')
#    parser.add_argument('destination', type=str, help='Destination CSV file')
    args = parser.parse_args()

    if (args.test):
        unittest.main()
        sys.exit()

    processor = Processor()
    parser = VArchCParser(processor)
    parser.ParseFile(args.source)
    print parser.processor
