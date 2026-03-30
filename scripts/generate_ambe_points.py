#!/usr/bin/env python3
"""
Generate ambe_points.mac from ambe_spectrum.txt
Assumes ambe_spectrum.txt lines: <energy> <weight> [# comment]
Outputs /gps/hist/point <E> <W_normalized> MeV
"""
import sys, math, os

infile = "ambe_spectrum.txt"
outmac  = "ambe_points.mac"

if not os.path.exists(infile):
    print("Input file not found:", infile); sys.exit(1)

pts=[]
with open(infile) as f:
    for ln in f:
        ln = ln.split('#',1)[0].strip()
        if not ln: continue
        cols = ln.split()
        try:
            e = float(cols[0])
            w = float(cols[1])
            pts.append((e,w))
        except Exception as ex:
            # skip malformed lines
            continue

if not pts:
    print("No numeric data found in", infile); sys.exit(1)

tot = sum(w for e,w in pts)
if tot <= 0:
    print("Total weight <= 0:", tot); sys.exit(1)

with open(outmac,"w") as fo:
    fo.write("# Auto-generated from %s\n" % infile)
    fo.write("/gps/hist/type energy\n")
    fo.write("/gps/hist/point clear\n")
    for e,w in pts:
        wnorm = w / tot
        fo.write("/gps/hist/point %.6g %.12g MeV\n" % (e, wnorm))
    fo.write("\n# End\n")

print("Wrote", outmac, "points=", len(pts), "sum(weights)=", sum(w for e,w in pts)/tot)
