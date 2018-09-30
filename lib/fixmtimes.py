# Tinderbox decides which packages to rebuild by asking make(1).  Often you
# would have to wait a long time to test your changes to some port while it
# is busy needlessly rebuilding packages just because some of their sources
# went out of date.  Mend this stupidity by adjusting mtimes of those until
# make(1) no longer suggests doing useless rebuilds.
#
# Add the following lines into `lib/tc_command.sh' (around line 2012) after
# creating of the Makefile and put this Python script itself under `lib/':
#
#    echo -n "checking package mtimes to avoid needless rebuilds... "
#    while (cd ${pkgDir}/All && make -dm -n \
#        -f ../../../builds/${build}/Makefile 2>&1 | \
#        python ../../../lib/fixmtimes.py); do
#            echo -n "rechecking after adjustment round... "
#    done ; echo done

import os, re, sys

# `t.z' because we want to support different package formats
modified_before = re.compile(r'Examining (.*?\.t.z)\.\.\.modified .*?[0-9]\.\.\.modified before source (.*?\.t.z)')

need_rerun = False
first_match = True

for line in sys.stdin:
    m = modified_before.match(line)
    if m:
        if first_match:
            print
            first_match = False
        tgt = m.group(1)
        src = m.group(2)
        print " * %s is older than %s" % (tgt, src)
        try:
            tmt, tat = int(os.stat(tgt).st_mtime), int(os.stat(tgt).st_atime)
            smt, sat = int(os.stat(src).st_mtime), int(os.stat(src).st_atime)
        except OSError:
            continue
        if (tmt < smt):
            print "   adjusting mtime (%d -> %d, %+d)" % (tmt, smt, smt - tmt)
            os.utime(tgt, (sat, smt))
            need_rerun = True

sys.exit(not need_rerun)
