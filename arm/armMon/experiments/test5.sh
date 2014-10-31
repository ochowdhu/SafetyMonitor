## script to run tests
## TEST5 -- full vs normal logic with formulas that should be the same in both

testdir=test5
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""


ntests=5
formulas=("allT" "allF" "alt1" "allT \$\$0,10\$\$ perT10" "allT \$0,10\$ perT10" "((~perT3) \$\$0,2\$\$ perT3)" "alt1 || (~alt1)" "(~alt1) || alt1")

for ((f=0;f<${#formulas[@]};f++))
do

	# grab formula
	cform=${formulas[f]}
	echo "Starting formula \"$cform\""

	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting full run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv" -f >> "$testdir/pTrace50m-full-f$f.log" 2>&1
	done
	sleep 1

	### loop both
	for ((i=0;i<$ntests;i++))
	do
		echo "$i: starting restricted run..."
		bash "$codedir/runArmMon.sh" "$cform" "pTrace50m.csv"  >> "$testdir/pTrace50m-rest-f$f.log" 2>&1
	done
	sleep 1


done
