## script to run tests
## TEST2

testdir=test2
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""


ntests=3
formulas=("<0,10> alt1" "<0,50> alt1" "<0,100> alt1" "<0,500> alt1" "<0,1000> alt1" "<0,15000> alt1")

for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	### loop aggr
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting aggr run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -a -f >> "$testdir/pTrace50m-2a-af-f$f.log" 2>&1
	done

	sleep 1
	### loop cons
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting cons run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -c -f >> "$testdir/pTrace50m-2a-cf-f$f.log" 2>&1
	done
	sleep 1

	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting cons run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -f >> "$testdir/pTrace50m-2a-bf-f$f.log" 2>&1
	done
	sleep 1
done
