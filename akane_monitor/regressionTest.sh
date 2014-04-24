## Regression test, running through all Omar's traces

traceDir=omarTraces

#invar="x -> ( <0, 5> (<0, 5> (<<0, 10>> (p))))"
#./runMon.sh "$invar" "$traceDir/trace1.txt" $1 1 
#echo "@@@@ TRACE 1: Should be SATISFIED"
#
#invar="x -> [0, 2] ((p) \$0,4\$ (<0, 2> (q)) )"
#./runMon.sh "$invar" "$traceDir/trace2.txt" $1 1 
#echo "@@@@ TRACE 2: Should be SATISFIED"
#./runMon.sh "$invar" "$traceDir/trace3.txt" $1 1 
#echo "!!!! TRACE 3: Should be VIOLATED"
#
#invar="x -> <0, 1> ( <<0,2>> (<0,3> (<<0,4>> (q))))"
#./runMon.sh "$invar" "$traceDir/trace4.txt" $1 1 
#echo "@@@@ TRACE 4: Should be SATISFIED"
#./runMon.sh "$invar" "$traceDir/trace5.txt" $1 1 
#echo "@@@@ TRACE 5: Should be SATISFIED"
#
#invar="x -> <1, 1> (<<1, 2>> (<1, 3> (<<1, 4>> (q))))"
#./runMon.sh "$invar" "$traceDir/trace5.txt" $1 1 
#echo "@@!! TRACE 5: Omar thinks VIOLATED, Should be SATISFIED"
#
#invar="x -> <0, 4> (((p || q) || <<0, 6>> (r)) || <0, 1> (z))"
#./runMon.sh "$invar" "$traceDir/trace6.txt" $1 1 
#echo "@@@@ TRACE 6: Should be SATISFIED"
#
#invar="x -> <0, 1> ( (a) \$\$0, 5\$\$ (<0, 2> (b)))"
#./runMon.sh "$invar" "$traceDir/trace7.txt" $1 1 
#echo "@@@@ TRACE 7: Should be SATISFIED"
#echo "@@@@ Edited trace to make satisfied, was wrong"
#
#invar="x -> ([0, 1] (a)) \$0, 5\$ (<0, 2> (b)) "
#./runMon.sh "$invar" "$traceDir/trace8.txt" $1 1 
#echo "@@@@ TRACE 8: Should be SATISFIED"
#./runMon.sh "$invar" "$traceDir/trace9.txt" $1 1 
#echo "!!!! TRACE 9: Should be VIOLATED"



echo "OMAR SINCE REGRESSION...."

#invar="x -> (p) \$0,5\$ ([[1,1]] (q))"
invar="x -> (p) \$0,5\$ ((q))"
./runMon.sh "$invar" "$traceDir/S1-S-1.csv" $1 1
echo "@@@@ TRACE 1: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S1-S-2.csv" $1 1
echo "@@@@ TRACE 2: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S1-S-3.csv" $1 1
echo "@@@@ TRACE 3: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S1-S-4.csv" $1 1
echo "@@@@ TRACE 4: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S1-S-5.csv" $1 1
echo "@@@@ TRACE 5: Should be SATISFIED"
	./runMon.sh "$invar" "$traceDir/S1-S-6.csv" $1 
echo "@@@@ TRACE 6: Should be SATISFIED"
echo "=============================================="
echo "NOW, VIOLATING TRACES"
./runMon.sh "$invar" "$traceDir/S1-V-1.csv" $1 1
echo "!!!! TRACE 1: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S1-V-2.csv" $1 1
echo "!!!! TRACE 2: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S1-V-3.csv" $1 1
echo "!!!! TRACE 3: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S1-V-4.csv" $1 1
echo "!!!! TRACE 4: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S1-V-5.csv" $1 1
echo "!!!! TRACE 5: Should be VIOLATED"

echo "====================================="
echo "END S1, NOW S3 (S2 broken traces...)"
echo "====================================="
invar="x -> ((p) \$0,5\$ (q)) \$0,5\$ ((r) \$0,5\$ (t))"
#invar="x -> ( ((p) \$0,5\$ ([[1,1]] (q))) \$0,5\$ ([[1,1]] ((r) \$0,5\$ ([[1,1]] (t)))))"
./runMon.sh "$invar" "$traceDir/S3-S-1.csv" $1 1
echo "@@@@ TRACE 1: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-2.csv" $1 1
echo "@@@@ TRACE 2: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-3.csv" $1 1
echo "@@@@ TRACE 3: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-4.csv" $1 1
echo "@@@@ TRACE 4: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-5.csv" $1 1
echo "@@@@ TRACE 5: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-6.csv" $1 1
echo "@@@@ TRACE 6: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-7.csv" $1 1
echo "@@@@ TRACE 7: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-8.csv" $1 1
echo "@@@@ TRACE 8: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-9.csv" $1 1
echo "@@@@ TRACE 9: Should be SATISFIED"
./runMon.sh "$invar" "$traceDir/S3-S-10.csv" $1 1
echo "@@@@ TRACE 10: Should be SATISFIED"
echo "==========================================="
echo "NOW, VIOLATED TRACES"
./runMon.sh "$invar" "$traceDir/S3-V-1.csv" $1 1
echo "!!!! TRACE 1: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-2.csv" $1 1
echo "!!!! TRACE 2: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-3.csv" $1 1
echo "!!!! TRACE 3: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-4.csv" $1 1
echo "!!!! TRACE 4: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-5.csv" $1 1
echo "!!!! TRACE 5: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-6.csv" $1 1
echo "!!!! TRACE 6: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-7.csv" $1 1
echo "!!!! TRACE 7: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-8.csv" $1 1
echo "!!!! TRACE 8: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-9.csv" $1 1
echo "!!!! TRACE 9: Should be VIOLATED"
./runMon.sh "$invar" "$traceDir/S3-V-10.csv" $1 1
echo "!!!! TRACE 10: Should be VIOLATED"
