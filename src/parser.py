#!/usr/bin/python

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
        group = self.processor.FindGroup(tokens[0])
        if group != None:
            group.SetFailure(failure)
        else:
            instruction = self.processor.FindInstruction(tokens[0])
            if instruction != None:
                instruction.SetFailure(failure)
            else:
                self.VArchCError('Could not find symbol to set target. Ignoring ', tokens[0], str, loc)

    def SetProcessorName(self, str, loc, tokens):
        self.processor.SetName(tokens[1])

    def SetProcessorWordsize(self, str, loc, tokens):
        self.processor.SetWordsize(tokens[1])

    def SetTarget(self, str, loc, tokens):
        group = self.processor.FindGroup(tokens[0])
        if group != None:
            group.SetTarget(tokens[1])
        else:
            instruction = self.processor.FindInstruction(tokens[0])
            if instruction != None:
                instruction.SetTarget(tokens[0])
            else:
                self.VArchCError('Could not find symbol to set target. Ignoring ' + tokens[0], str, loc)

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
    __e = pp.CaselessLiteral('E')

    __comment1 = pp.Literal('//').suppress() + pp.restOfLine.suppress()
    __comment2 = pp.Literal('/*').suppress() + pp.SkipTo(pp.Literal('*/'), include = True)
    __comment3 = pp.Literal('#').suppress() + pp.restOfLine.suppress()

    __comments = __comment1 | __comment2 | __comment3

    __unit = ['K', 'M', 'G', 'T']
    # ID = [a-zA-Z][_a-zA-Z0-9]*
    __symbol = pp.Word(pp.alphas, pp.alphanums + '_').setName('symbol')
    __str = __quotes + pp.SkipTo(__quotes, include=True)

    # INT = [0-9]+
    __plusorminus = pp.Literal('+') | pp.Literal('-')
    __int = pp.Combine(pp.Optional(__plusorminus) + pp.Word(pp.nums))

    # HEX = (0x | 0X) [0-9a-fA-F]+
    __hexnumber = pp.Combine((pp.Literal('0x').suppress() | pp.Literal('0X').suppress()) + pp.Word(pp.nums + 'abcdefABCDEF'))
    __hexnumber.setName('hexadecimal number')

    # NUM = ([0-9]+ | HEX)
    __number = (__int ^ __hexnumber).setName('number')

    # FP_Num
    __fpNum = pp.Combine(__int + pp.Optional(__dot + pp.Word(pp.nums)) + pp.Optional(__e + __int ))

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

    __processorClause = pp.Literal('processor') + __symbol + __semiColon
    __processorClause.setParseAction(actions.SetProcessorName)

    __wordsizeClause = pp.Literal('wordsize') + __int + __semiColon
    __wordsizeClause.setParseAction(actions.SetProcessorWordsize)

    __targetClause = __symbol + pp.Literal('target').suppress() + pp.Literal('is').suppress() + __symbol + __semiColon
    __targetClause.setParseAction(actions.SetTarget)

    __varchc_token = __importClause | __instructionClause | __groupClause | __inputClause | \
                     __failureClause | __processorClause | __wordsizeClause | __targetClause

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
    unittest.main()
