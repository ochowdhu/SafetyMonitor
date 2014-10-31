## script to run tests
## TEST7 -- checking list vs ints worst case list

testdir=test7
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""


ntests=3
formulas=("<0,10> allF" "<0,50> allF" "<0,100> allF" "<0,500> allF" "<0,1000> allF" "<0,15000> allF")

for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	### loop aggr
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting int run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" >> "$testdir/allF-f$f.log" 2>&1
	done

	sleep 1
	### loop cons
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting list run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -l >> "$testdir/allF-f$f.log" 2>&1
	done
	sleep 1

done
