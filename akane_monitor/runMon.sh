#!/bin/bash
# single script to run monitor on a formula
# classpath is set on afs to find MonTranslate

echo $1
formula=$(echo "$1" | java MonTranslate | python parse2ast.py | tail -n 1) 

echo "======================="
echo "Using formula: $formula"

python ./resMonitor.py "$formula" $2 $3

