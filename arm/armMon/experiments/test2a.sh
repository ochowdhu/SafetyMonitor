## script to run tests
## TEST2

testdir=test2
bindir=../src/build
#tracedir=../traces/
tracedir=""


ntests=3
formulas=("<0,10> alt1" "<0,50> alt1" "<0,100> alt1" "<0,500> alt1" "<0,1000> alt1" "<0,15000> alt1")


for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	##### loop conservative
	for ((i=0;i<$ntests;i++))
	do
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-2a-bf-f$f.log" 2>&1
		echo "$i: starting run..."
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -f >> "$testdir/pTrace50m-2a-bf-f$f.log" 2>&1
		echo "$i: finished run..."
	done
	echo "$i: finished \"-f\" tests for \"$cform\""

	##### loop both
	for ((i=0;i<$ntests;i++))
	do
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-2a-af-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -a -f >> "$testdir/pTrace50m-2a-af-f$f.log" 2>&1
		echo "$i: finished run..."
	done
	echo "$i: finished \"-a -f\" tests for \"$cform\""

	#### loop aggr
	for ((i=0;i<$ntests;i++))
	do
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-2a-cf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -c -f >> "$testdir/pTrace50m-2a-cf-f$f.log" 2>&1
		echo "$i: finished run..."
	done
	echo "$i: finished \"-c -f\" tests for \"$cform\""

done # outer formula loop
