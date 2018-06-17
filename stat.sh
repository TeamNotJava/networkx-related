#!/bin/sh
#Run the script
#chmod +x stat.sh
#./stat.sh "your comand (e.g. python3 framework_test.py --closure)" number_exec timeout
NUM_EXEC=$2
COUNT=0
TIMEOUT=$3
while [ "$COUNT" != "$NUM_EXEC" ]; do
    gtimeout $TIMEOUT $1 >> stat.log
    # gtimeout exists with status 124 if timeout
    if [ "$?" == 124 ]; then
        echo "timeout" >> stat.log
    elif [ "$?" == 137 ]; then
        # gtime exists with status 137 if some error in the code occured
        echo "error" >> stat.log
    else
        echo "" >> stat.log
    fi
    COUNT=$((COUNT+1))
done
