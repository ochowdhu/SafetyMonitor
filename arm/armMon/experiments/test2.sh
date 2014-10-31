## script to run tests
## TEST2

testdir=test2
bindir=../src/build
tracedir=../traces/

ntests=3
formulas=("<0,10> allF" "<0,50> allF" "<0,100> allF" "<0,500> allF" "<0,1000> allF" "<0,15000> allF")


for ((f=0;f<${#formulas[@]};f++))
do
		cform=${formulas[f]}
		echo "Starting formula \"$cform\""
	for ((i=0;i<$ntests;i++))
	do
		##########################################################
		### add separators
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-cf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-bf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-af-f$f.log" 2>&1

		echo "$i: starting run..."
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -f >> "$testdir/pTrace50m-bf-f$f.log" 2>&1
		echo "$i: finished \"-f\" tests for \"$cform\""

		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -a -f >> "$testdir/pTrace50m-af-f$f.log" 2>&1

		echo "$i: finished \"-a -f\" tests for \"$cform\""

		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -c -f >> "$testdir/pTrace50m-cf-f$f.log" 2>&1
		echo "$i: finished \"-c -f\" tests for \"$cform\""

		echo "$i: finished run..."
	done

done # outer formula loop
