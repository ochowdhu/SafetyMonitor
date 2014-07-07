#!/bin/bash
# single script to run monitor on a formula
# classpath is set on afs to find MonTranslate

formula=$(echo "$1" | ./parser/bflex/bmtl | tail -n 1)

echo "======================="
echo "Using formula: $formula"

python ./monRVTiming.py "$formula" $2 $3 $4
