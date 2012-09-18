#!/usr/bin/env python
# -*- python -*-

__description__ = 'Tool to create a PDF object graph'
__author__ = 'bacspace____'
__version__ = '0.0.1'
__date__ = '2012/09/17'

"""
Tool to create a PDF object graph

no Copyright
Use at your own risk

History:
  2012/09/17: start

Todo:

"""


import re
import sys
from collections import deque

import gv
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write


isint = re.compile('^\d+$')

def isWhiteSpace(code):
    """tell if code is white space
    code: decimal representation char code"""

    if (code == 0 or
        code == 9 or
        code == 10 or
        code == 12 or
        code == 13 or
        code == 32):
           return True
    return False

def isDelimiter(code):
    """tell if code is delimiter
    code: decimal representation char code"""
    if (code == 0x28
        or code == 0x29
        or code == 0x3C
        or code == 0x3E
        or code == 0x5B
        or code == 0x5D
        or code == 0x7B
        or code == 0x7D
        or code == 0x2F
        or code == 0x25):
        return True
    return False

def allNone(list):
    if (list[0] == None and
        list[1] == None and
        list[2] == None):
        return True
    return False

def isObjToken(list):
#    print list
    if (isint.match(list[0]) and
        isint.match(list[1]) and
        list[2] == "obj"):
        return True
    return False

def getObjNum(list):
    return list[0]

def isIndirect(list):
    if (isint.match(list[0]) and
        isint.match(list[1]) and
        list[2] == "R"):
        return True
    return False

def getIndirectNum(list):
    return list[0]


class Tokenizer:
    """ a part of this class is from pdf-parser.py
    http://didierstevens.com/files/software/pdf-parser_V0_3_9.zip
    """
    def __init__(self, file):
        self.file = file
        self.infile = open(file, 'rb')
        self.ungetted =[]
        self.position = -1

    def byte(self):
        if self.infile.closed:
            return None
        inbyte = self.infile.read(1)
        if not inbyte:
            self.infile.close()
            return None
        return ord(inbyte)

    def token(self):
        self.token_str = ''
        code = self.byte()
        while code != None:
            if isWhiteSpace(code) or isDelimiter(code):
                code = self.byte()
                continue
            else:
                self.token_str = self.token_str + chr(code)
                code = self.byte()

            if isWhiteSpace(code) or isDelimiter(code) or code == None:
                return self.token_str
            else:
                continue

        return None

def Main():
    pdf = sys.argv[1]
    output = "graph.png"
    if len(sys.argv) > 2:
        output = sys.argv[2]

    tk = Tokenizer(pdf)

    queue = deque([tk.token(), tk.token(), tk.token()])
    obj_num = ""
    gr = graph()

    while not allNone(queue):
        if isObjToken(queue):
            obj_num = getObjNum(queue)
            if not gr.has_node(obj_num):
                gr.add_node(obj_num)
        elif isIndirect(queue):
            if not gr.has_node(getIndirectNum(queue)):
                gr.add_node(getIndirectNum(queue))
            if not gr.has_edge((obj_num, getIndirectNum(queue))):
                gr.add_edge((obj_num, getIndirectNum(queue)))

        queue.popleft()
        queue.append(tk.token())

    dot = write(gr)
    gvv = gv.readstring(dot)
    gv.layout(gvv, 'dot')
    gv.render(gvv, 'png', output)

if __name__ == '__main__':
    Main()

