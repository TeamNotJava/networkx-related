#!/bin/bash
#Run the script
#chmod +x stat.sh
#./stat.sh "your comand (e.g. python3 framework_test.py --closure)" number_exec timeout
NUM_EXEC=$2
COUNT=0
TIMEOUT=$3
OS=$(uname)
#echo "$OS"

if [ "$OS" = "Darwin" ]; then
	while [ "$COUNT" != "$NUM_EXEC" ]; do
		ts=$(gdate +%s%N)
		gtimeout $TIMEOUT $1 >> stat.log
	    # gtimeout exits with status 124 if timeout
	    if [ "$?" == 124 ]; then
	    	echo "timeout" >> stat.log
	    elif [ "$?" == 137 ]; then
		# gtimeout exits with status 137 if some error in the code occured
		echo "error" >> stat.log
		else
			tt=$((($(gdate +%s%N) - $ts)/1000000))
			echo "$tt" >> stat.log
		fi
		COUNT=$((COUNT+1))
	done
fi
if [ "$OS" = "Linux" ]; then
	while [ "$COUNT" != "$NUM_EXEC" ]; do
		ts=$(date +%s%N)
		timeout $TIMEOUT $1 >> stat.log
	    # timeout exits with status 124 if timeout
	    if [ "$?" == 124 ]; then
	    	echo "timeout" >> stat.log
	    elif [ "$?" == 137 ]; then
		# timeout exits with status 137 if some error in the code occured
		echo "error" >> stat.log
		else
			tt=$((($(date +%s%N) - $ts)/1000000))
			echo "$tt" >> stat.log
		fi
		COUNT=$((COUNT+1))
	done
fi
