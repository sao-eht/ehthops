import sys
import os
import argparse
import numpy as np
import pandas as pd
from collections import OrderedDict
from eat.io import hops, util
from eat.hops import util as hu

def overlap(rstation, rzoom):
    return np.maximum(rzoom[0], rstation[0]) <= np.minimum(rzoom[1], rstation[1])

def contains(rstation, rzoom):
    return (rstation[0] <= rzoom[0]) and (rstation[1] >= rzoom[1])

def main():
    parser = argparse.ArgumentParser(description='Program to create a HOPS control file with notches')
    parser.add_argument('band', type=int, choices=[1,2,3,4], help='frequency band')
    parser.add_argument('fringefile', type=str, help='path to a non-NOEMA baseline fringe file for extracting zoom band information for the given band')
    parser.add_argument('freqfile', type=str, help='path to station frequency info file')
    parser.add_argument('station', type=str, help='station name to compute notches for (e.g. "NOEMA")')

    args = parser.parse_args()

    # get zoom band info
    try:
        p = hu.params(args.fringefile)
    except FileNotFoundError:
        print(f"{args.fringefile} does not exist! Exiting.")
        sys.exit(1)

    # get station freq info (e.g. for NOEMA)
    try:
        df = pd.read_csv(args.freqfile, delim_whitespace=True)
    except FileNotFoundError:
        print(f"{args.freqfile} does not exist! Exiting.")
        sys.exit(1)

    # get only the rows corresponding to given station
    df = df[df['station'] == args.station]

    # compute where phase jumps occur in zoom bands for NOEMA baselines
    freq_to_notch = [] # list of tuples to notch
    notchdict = OrderedDict()

    nchan = p.fedge.shape[0]
    for ch in range(nchan):
        f_lo_zoom = p.fedge[ch]
        f_hi_zoom = p.fedge[ch]+p.bw[ch]

        # TODO update the following to work for band 1
        stfreqs = [n for n in df.loedge_MHz if n < f_lo_zoom or n < f_hi_zoom]
        if not stfreqs:
            continue
        f_lo_station = max(stfreqs)
        f_hi_station = f_lo_station + df.bw_MHz[df.loedge_MHz == f_lo_station].to_numpy()[0]

        rzoom = (f_lo_zoom, f_hi_zoom)
        rstation = (f_lo_station, f_hi_station)

        # if the ranges overlap, the smaller section of the zoom band must be flagged
        if overlap(rstation, rzoom) and not contains(rstation, rzoom):
            if rstation[0] > rzoom[0]:
                if rstation[0] <= rzoom[0]+(p.bw[ch]/2.):
                    freq_to_notch.append((ch, (rzoom[0], rstation[0])))
                    notchdict[ch] = (rzoom[0], rstation[0])
                else:
                    freq_to_notch.append((ch, (rstation[0], rzoom[1])))
                    notchdict[ch] = (rstation[0], rzoom[1])
            else:
                if rstation[1] > rzoom[0]+(p.bw[ch]/2.):
                    freq_to_notch.append((ch, (rstation[1], rzoom[1])))
                    notchdict[ch] = (rstation[1], rzoom[1])
                else:
                    freq_to_notch.append((ch, (rzoom[0], rstation[1])))
                    notchdict[ch] = (rzoom[0], rstation[1])

    for k in notchdict.keys():
        print(f"notchdict[{k}] = {notchdict[k]}")

    # create control file with notches
    #for tup in freq_to_notch:
    #    print(tup)
    with open(f'cf1_notches_b{args.band}', 'w') as f:
        f.write(f"* Band {args.band}\n\n")

        if args.station == "NOEMA":
            f.write("if station N\n")
        else:
            print("No notches necessary for non-NOEMA stations! Exiting.")
            sys.exit(1)

        cmdflag = True
        for tup in freq_to_notch:
            if cmdflag:
                f.write(f"  notches {tup[1][0]} {tup[1][1]}\n")
                cmdflag = False
            else:
                f.write(f"          {tup[1][0]} {tup[1][1]}\n")

if __name__ == '__main__':
    main()

