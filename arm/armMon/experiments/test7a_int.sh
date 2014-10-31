## script to run tests
## TEST7a -- checking list vs ints best case

testdir=test7
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""

# worst case for ints would be <0,X> [0,1] alt1

ntests=3
formulas=("<0,10> (allT)" "<0,50> allT" "<0,100> allT" "<0,500> allT" "<0,1000> allT" "<0,15000> allT")

for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	### loop aggr
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting int run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" >> "$testdir/allT-f$f.log" 2>&1
	done

	sleep 1
	### loop cons
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting list run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -l >> "$testdir/allT-f$f.log" 2>&1
	done
	sleep 1

done
