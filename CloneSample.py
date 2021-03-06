#
# Code to remove one sample from the datacard
#

import re
from sys import argv
import os.path
from optparse import OptionParser
from math import sqrt,fabs

parser = OptionParser()
parser.add_option("-i", "--input",  dest="nameFileChange", help="file with samples to remove (e.g. ttH)", default='blabla.py')
parser.add_option("-o", "--output", dest="nameOutFileDC",  help="file where to dump the new DC", default='test.txt')

(options, args) = parser.parse_args()
options.bin = True # fake that is a binary output, so that we parse shape lines
options.noJMax = False
options.nuisancesToExclude = ''
options.stat = False


nameFactor = {}
if os.path.exists(options.nameFileChange):
    handle = open(options.nameFileChange,'r')
    exec(handle)
    handle.close()
print "nameFactor = ", nameFactor

import sys
sys.path.append('tools')
from DatacardParser import *

DC = parseCard(file(args[0]), options)
nuisToConsider = [ y for y in DC.systs ]



# copy header
# everything up to "observation", included

lines = open (args[0], 'r').read().split ('\n')

header = []

foundObservation = 0
for line in lines:
  if (foundObservation == 0) : header.append (line)
  tempLine = line.split (' ')
  tempLine = filter(lambda a: a != '', tempLine)
  if len(tempLine)>0  and   tempLine[0] == 'observation' :
      foundObservation = 1


print header

# write new datacard
filename = options.nameOutFileDC
f = open(filename, 'w')

# header
for line in header: f.write (line + '\n')
f.write ("---------------------------------------------------------------------------------------------------- \n")
# bin name
f.write ("bin                                 ")
for channel in DC.exp:
    for process in DC.exp[channel]:
        f.write ("%13s " % channel)
    if (channel in nameFactor.keys())  : # in this channel ther are some processes to clone
        for processTocClone in nameFactor[channel]:
            f.write ("%13s " % channel)
f.write("\n")

# process names (a.k.a. process)
f.write ("process                            ")
for channel in DC.exp:
    for process in DC.exp[channel]:
        f.write ("%13s " % process)
    if (channel in nameFactor.keys())  : # in this channel ther are some processes to clone
        for processTocClone in nameFactor[channel]:
            f.write ("%13s " % processTocClone[1])

f.write("\n")

# indices numbers: -1  0  1  2  3 ...
f.write ("process                            ")
for channel in DC.exp:
    numSig = 0
    numBkg = 1
    for process in DC.exp[channel]:
        if DC.isSignal[process] :
            f.write ("%13d " % numSig)
            numSig = numSig - 1
        else :
            f.write ("%13d " % numBkg)
            numBkg = numBkg + 1
    if (channel in nameFactor.keys())  : # in this channel ther are some processes to clone
        for processTocClone in nameFactor[channel]:
            if DC.isSignal[processTocClone[0]] :
                f.write ("%13d " % numSig)
                numSig = numSig - 1
            else :
                f.write ("%13d " % numBkg)
                numBkg = numBkg + 1

f.write("\n")

# rate
f.write ("rate ")
for channel in DC.exp:
    for process in DC.exp[channel]:
        f.write ("%9.4f " % DC.exp[channel][process] )
    if (channel in nameFactor.keys())  : # in this channel ther are some processes to clone
        for processTocClone in nameFactor[channel]:
            f.write ("%9.4f " % DC.exp[channel][processTocClone[0]] )

f.write("\n")

# systematics
## list of [(name of uncert, boolean to indicate whether to float this nuisance or not, type, list of what additional arguments (e.g. for gmN), keyline element)]
for nuis in nuisToConsider:
    f.write ("%25s" % nuis[0]) # name
    if nuis[2] != 'gmN':
        f.write ("%10s" % nuis[2]) #lnN
    else :
        f.write ("%5s" % nuis[2]) # gmN
        f.write ("%5s" % nuis[3][0]) # Ncontrol

    f.write (" ")

    for channel in DC.exp:
        for process in DC.exp[channel]:
            if channel in nuis[4]:
                if process in nuis[4][channel] :
                    if not isinstance ( nuis[4][channel][process], float ) :
                    # [0.95, 1.23]  ---> from 0.95/1.23
                        f.write ("   {0:4.3f}/{1:4.3f}".format(nuis[4][channel][process][0], nuis[4][channel][process][1]))
                    else :
                        if (nuis[4][channel][process] != 0) :
                            f.write ("%9.4f" % nuis[4][channel][process])
                        else :
                            f.write ("%13s" % "-")
                else :
                    f.write ("%13s" % "-")
            else :
                f.write ("%13s" % "-")

        if (channel in nameFactor.keys())  : # in this channel ther are some processes to clone
            for processTocClone in nameFactor[channel]:
                if processTocClone[0] in nuis[4][channel] :
                    if not isinstance ( nuis[4][channel][processTocClone[0]], float ) :
                    # [0.95, 1.23]  ---> from 0.95/1.23
                        f.write ("   {0:4.3f}/{1:4.3f}".format(nuis[4][channel][processTocClone[0]][0], nuis[4][channel][processTocClone[0]][1]))
                    else :
                        if (nuis[4][channel][processTocClone[0]] != 0) :
                            f.write ("%9.4f" % nuis[4][channel][processTocClone[0]])
                        else :
                            f.write ("%13s" % "-")
                else :
                    f.write ("%13s" % "-")
            else :
                f.write ("%13s" % "-")


    f.write("\n")
f.close ()




