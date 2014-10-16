## runArmMon.sh -- add formula, compile, and run formula

basepath=~/Private/research/
#basepath=~/Documents/Work/

formula=$1
tracedir="$basepath/thesis/SafetyMonitor/arm/armMon/traces"
confdir="$basepath/thesis/SafetyMonitor/arm/armMon-confbuild"
builddir="$basepath/thesis/SafetyMonitor/arm/armMon/src/build"
codedir="$basepath/thesis/SafetyMonitor/arm/armMon/src"

#args="-DDO_MON_CONS=0 -DDO_MON_AGGR=0"
#if [ -z "$3" ]
#	then
#if [ "$3" == "cons" ]
#	then 
#	args="-DDO_MON_CONS=1 -DDO_MON_AGGR=0"
#fi
#if [ "$3" == "aggr" ]
#	then
#	args="-DDO_MON_CONS=0 -DDO_MON_AGGR=1"
#fi
#fi

# generate config
cd $codedir
#echo "$1" | "$confdir/bmtl" "$4" > /dev/null 2>&1
#echo -e "$1" | "$confdir/bmtl2" "$4" > /dev/null 2>&1
printf "$1\n" | "$confdir/bmtl2" "${@:3}" > /dev/null 2>&1

echo "Calling BMTL with args \"${@:3}\""

cd $builddir
#cmake $args ../
make
./pc-armMon "$tracedir/$2"

