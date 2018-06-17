#!/bin/sh
#Run the script
#chmod +x stat.sh
#./stat.sh "your comand (e.g. python3 framework_test.py --closure)" number_exec timeout
NUM_EXEC=$2
COUNT=0
TIMEOUT=$3
while [ "$COUNT" != "$NUM_EXEC" ]
do
#($1 >> stat.log) & (sleep $TIMEOUT; echo "timeout" >> stat.log); kill $! 2> /dev/null || :
gtimeout $TIMEOUT $1 >> stat.log
echo "\n" >> stat.log
COUNT=$((COUNT+1))
done
