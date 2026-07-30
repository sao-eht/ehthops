#!/usr/bin/env bash

# Delete all data products leaving the repo in a clean state
stages=("0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close" "6.uvfits" "7.+apriori" "8.+polcal")

for stage in ${stages[@]}
do
    echo "Cleaning up $stage..."
    pushd $stage
    rm -rf tests temp log data cf*
    rm version

    if [ $stage == "1.+flags+wins" ]
    then
	rm bin/[0-6]* bin/9*
	rm pc*.pdf
    elif [[ $stage == "6.uvfits" || $stage == "7.+apriori" || $stage == "8.+polcal" ]]
    then
	    rm -rf 3*
	    rm *.h5 *.pickle
    if [[ $stage == "7.+apriori" || $stage == "8.+polcal" ]]
	then
        rm bin/*.import
	    rm bin/*.average
	fi
	if [ $stage == "7.+apriori" ]
	then
    	    rm -rf SEFD
	fi
	if [ $stage == "8.+polcal" ]
	then
    	    rm bin/0.launch
	fi
    elif [ $stage != "0.bootstrap" ]
    then
        if [ $stage != "5.+close" ]
        then
	    rm bin/[0-6]* bin/9*
        else
	    rm bin/[0-6]*
        fi
    else
	:
    fi

    popd
done
