#!/bin/bash
# single script to run monitor on a formula
# classpath is set on afs to find MonTranslate

echo $1
formula=$(echo "$1" | java -cp ../../antlr/MonLogic/ MonTranslate | python parse2ast.py | tail -n 1)

echo "======================="
echo "Using formula: $formula"

#python ./resMonitor.py "$formula" $2 $3
#python ./nresMonitor.py "$formula" $2 $3
#python ./nresMonitor2.py "$formula" $2 $3

#python -m cProfile ./monRVTiming.py "$formula" $2 $3 $4
#/usr/bin/time -v python ./monRVTiming.py "$formula" $2 $3 $4
python ./monRVTiming.py "$formula" $2 $3 $4
