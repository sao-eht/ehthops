#!/usr/bin/env bash

# clean up repo of all data products
stages=("0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close" "6.uvfits")

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
    elif [ $stage == "6.uvfits" ]
    then
	rm -rf 3*
	rm vis*
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
