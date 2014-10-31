## bash script to extra data from log files
awk '
	/^TIME/ { 
		total+=($3/$13); incr+=($5/$13); pol+=($7/$13); cons+=($9/$13); agg+=($11/$13); lines++;
	} 
	END { 
		print "l:" lines "\nt: " total/lines/1e9 "\ninc: " incr/lines/1e9 "\ncons: " cons/lines/1e9 "\nagg: " agg/lines/1e9
	}' $1

