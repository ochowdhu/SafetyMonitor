## script to run tests

testdir=test1
bindir=../src/build
tracedir=../traces/

ntests=5
formulas=("allT" "allF" "<0,10> allT" "<0,10> allF" "[0,10] allT" "[0,10] allF")


for ((f=0;f<${#formulas[@]};f++))
do
		cform=${formulas[f]}
		echo "Starting formula \"$cform\""
	for ((i=0;i<$ntests;i++))
	do
		##########################################################
		### add separators
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace5m-cf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace10m-cf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-cf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace100m-cf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace500m-cf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace1000m-cf-f$f.log" 2>&1

		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace5m-bf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace10m-bf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-bf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace100m-bf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace500m-bf-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace1000m-bf-f$f.log" 2>&1

		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace5m-af-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace10m-af-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace50m-af-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace100m-af-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace500m-af-f$f.log" 2>&1
		printf "\n\nRUN %d\n" "$i" >> "$testdir/pTrace1000m-af-f$f.log" 2>&1


		echo "$i: starting run..."
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace5m.csv" -f >> "$testdir/pTrace5m-bf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace10m.csv" -f >> "$testdir/pTrace10m-bf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -f >> "$testdir/pTrace50m-bf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace100m.csv" -f >> "$testdir/pTrace100m-bf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace500m.csv" -f >> "$testdir/pTrace500m-bf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace1000m.csv" -f >> "$testdir/pTrace1000m-bf-f$f.log" 2>&1
		echo "$i: finished \"-f\" tests for \"$cform\""

		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace5m.csv" -a -f >> "$testdir/pTrace5m-af-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace10m.csv" -a -f >> "$testdir/pTrace10m-af-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -a -f >> "$testdir/pTrace50m-af-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace100m.csv" -a -f >> "$testdir/pTrace100m-af-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace500m.csv" -a -f >> "$testdir/pTrace500m-af-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace1000m.csv" -a -f >> "$testdir/pTrace1000m-af-f$f.log" 2>&1
		echo "$i: finished \"-a -f\" tests for \"$cform\""

		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace5m.csv" -c -f >> "$testdir/pTrace5m-cf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace10m.csv" -c -f >> "$testdir/pTrace10m-cf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace50m.csv" -c -f >> "$testdir/pTrace50m-cf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace100m.csv" -c -f >> "$testdir/pTrace100m-cf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace500m.csv" -c -f >> "$testdir/pTrace500m-cf-f$f.log" 2>&1
		bash $bindir/../runArmMon.sh "$cform" "$tracedir/pTrace1000m.csv" -c -f >> "$testdir/pTrace1000m-cf-f$f.log" 2>&1
		echo "$i: finished \"-c -f\" tests for \"$cform\""

		echo "$i: finished run..."
	done

done # outer formula loop
