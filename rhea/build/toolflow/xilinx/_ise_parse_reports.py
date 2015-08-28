#
# Copyright (c) 2014-2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function

from myhdl import enum

#from .._report_parser import ReportParser

def get_utilization(fn=None):    
    """ parse the device resource utilization from the logs

    @todo : the following is fairly ugly and not the most 
       reliable.  There are xml files create (xrp) that would
       be a better source for the utilization - once the xlm
       package is understood these reports can be used instead
       of the log.
    """


    log = open(fn, 'r')
    info = {}
    info['syn'] = {}
    fmax = []
    States = enum('search', 'slc_util', 'io_util', 'ip_util')
    state = States.search

    for ln in log:
        if 'Maximum Frequency:' in ln:
            if len(ln.split(':')) < 3:
                   continue
            fstr = ln.split(':')[2]
            fstr = fstr.replace(')', '')        
            fstr = fstr.replace(' ', '')
            fstr = fstr.strip()
            fmax.append(fstr)
    
        # @todo: probalby better to parse the XML files!
        # synthesis gives results in a table
        #   Slice Logic Utilization:
        #   IO Utilization:
        #   Specific Feature Utilization:
        #    <name>: X out of Y <percent>
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if state == States.search:
            if 'Slice Logic Utilization' in ln:
                state = States.slc_util
                lncnt = 1  
                #print(ln)
            elif 'Specific Feature Utilization' in ln:
                state = States.ip_util
                lncnt = 1
                #print(ln)
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        elif state == States.slc_util:
            ln = ln.strip()
        
            if lncnt in (1,7):
                # check sliptls
                print(ln)
                sp1 = ln.split(':')
                sp2 = sp1[1].split()
                if len(sp1) != 2 or len(sp2) != 5:
                    state = States.search
                    continue  # jump to the next line
        
                #print(lncnt, ln)
                nm,outof = ln.split(':')
                x,out,of,y,p = outof.split()
                #print(x,out,of,y,p)
                x = x.replace(',', '')
                y = y.replace(',', '')
                p = p.replace('%', '')
        
            if lncnt == 1:
                info['syn']['reg'] = tuple(map(int, (x,y,p,)))
            elif lncnt == 7:
                info['syn']['lut'] = tuple(map(int, (x,y,p,)))
            elif lncnt >= 10:
                state = States.search
        
            lncnt += 1
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        elif state == States.ip_util:
            ln = ln.strip()
        
            if lncnt in (1,2,16):
                #print(ln)
                # check sliptls
                sp1 = ln.split(':')
                if len(sp1) != 2:
                    state = States.search                    
                    continue
                sp2 = sp1[1].split()
                if len(sp2) != 5:
                    state = States.search
                    continue  # jump to the next line
        
                #print(lncnt, ln)
                nm,outof = ln.split(':')
                x,out,of,y,p = outof.split()
                #print(x,out,of,y,p)
                x = x.replace(',', '')
                y = y.replace(',', '')
                p = p.replace('%', '')
        
            if lncnt == 1:    # RAMB16B
                pass
            elif lncnt == 2:  # RAMB8B
                pass
            elif lncnt == 16: # DSP48
                #print(x,out,of,y,p)
                info['syn']['dsp'] = tuple(map(int, (x,y,p,)))
            elif lncnt >= 22:
                state = States.search
            lncnt += 1

        # end of parsing state-machine
        
    if len(fmax) > 0:
        info['fmax'] = fmax[-1]
    else:
        info['fmax'] = -1
    
    return info

