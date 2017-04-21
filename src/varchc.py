#!/usr/bin/python

import argparse
import sys
import unittest

from parser import VArchCParser
from processor import Processor

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='VArchC: Generate Variation Aware ArchC Post-Behavior Models')
#    parser.add_argument('-d', '--dblp', action='store_true', help='Fetch DBLP Canonical name')
    parser.add_argument('-i', '--input', type=str, help='Define input parameter (eg: -i p=5)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode, dump the input parsed file contents')
#    parser.add_argument('-s', '--sleep', type=int, help='Sleep time in seconds between web queries (default: 20)')
    parser.add_argument('source', type=str, help='Source VArchC file (.vac)')
#    parser.add_argument('destination', type=str, help='Destination CSV file')
    args = parser.parse_args()

    processor = Processor()
    parser = VArchCParser(processor)
    parser.ParseFile(args.source)

    if args.verbose:
        print parser.processor

    processor.SaveCode()
