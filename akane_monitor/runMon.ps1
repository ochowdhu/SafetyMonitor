$formula = echo $args[0] | java MonTranslate | python parse2ast.py | Select-Object -Last 1
echo "=================="
echo "Using formula: $formula"

python ./resMonitor.py "$formula" $args[1] $args[2]