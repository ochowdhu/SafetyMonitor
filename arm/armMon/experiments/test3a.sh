## script to run tests
## TEST3 -- showing list vs intervals 

testdir=test3
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""


ntests=3
formulas=("<0,10> allF" "<0,100> allF" "<0,500> allF" "<0,10> alt1" "<0,100> alt1" "<0,500> alt1" "<0,10> allT" "<0,100> allT" "<0,500> allT")

for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	### loop both
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting int run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv"  >> "$testdir/pTrace50m-3a-int-f$f.log" 2>&1
	done
	sleep 1

	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting int run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -l >> "$testdir/pTrace50m-3a-list-f$f.log" 2>&1
	done
	sleep 1

done
