## script to run tests
## TEST6a -- full vs normal logic growing the # of formulas

testdir=test6
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""


ntests=5
formulas=("(((allF || allT) || alt1) || perT10)" "(((allF || allT) || alt1) && perT10)" "(((allF || allT) && alt1) && perT10)" "(((allF && allT) && alt1) && perT10)")

for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting full run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m-custom.csv" -f >> "$testdir/pTrace50m-full-f$f.log" 2>&1
		grep "NFORMULAS" "$codedir/gendefs.h" >> "$testdir/pTrace50m-full-f$f.log"
	done
	sleep 1

	### loop both
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting restricted run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m-custom.csv"  >> "$testdir/pTrace50m-rest-f$f.log" 2>&1
		grep "NFORMULAS" "$codedir/gendefs.h" >> "$testdir/pTrace50m-rest-f$f.log"
	done
	sleep 1


done
