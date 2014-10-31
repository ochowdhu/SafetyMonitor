## script to run tests
## TEST4 -- full vs normal logic

testdir=test4
bindir=../src/build
codedir=../src/
#tracedir=../traces/
tracedir=""


ntests=3
formulas=("allT \$\$0,10\$\$ allF" "allT \$0,10\$ allF" "<0,10> allF" "<0,100> allF" "<0,500> allF" "alt1 || [1,1] alt1" "alt1 && [1,1] alt1]" "<0,10> perT10 && [1,9] ~perT10")

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
