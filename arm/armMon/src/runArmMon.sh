## runArmMon.sh -- add formula, compile, and run formula

formula=$1
tracedir=~/Private/research/thesis/SafetyMonitor/arm/armMon/traces
confdir=~/Private/research/thesis/SafetyMonitor/arm/armMon-confbuild
builddir=~/Private/research/thesis/SafetyMonitor/arm/armMon/src/build
codedir=~/Private/research/thesis/SafetyMonitor/arm/armMon/src

args="-DDO_MON_CONS=0 -DDO_MON_AGGR=0"
#if [ -z "$3" ]
#	then
if [ "$3" == "cons" ]
	then 
	args="-DDO_MON_CONS=1 -DDO_MON_AGGR=0"
fi
if [ "$3" == "aggr" ]
	then
	args="-DDO_MON_CONS=0 -DDO_MON_AGGR=1"
fi
#fi

# generate config
cd $codedir
echo "$1" | "$confdir/bmtl" > /dev/null 2>&1

echo "USING ARGS $args"

cd $builddir
cmake $args ../
make
./pc-armMon "$tracedir/$2"

