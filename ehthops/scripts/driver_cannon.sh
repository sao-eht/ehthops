# set up envs
source $HOME/.bashrc
mamba activate ehthops310
source /n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/installed/hops-3.24/bin/hops.bash

stages=("0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close" "6.uvfits")

for stage in ${stages[@]}
do
    echo "Starting stage $stage..."
    cd $stage
    echo "cd into $(pwd)"

    if [ $stage != "6.uvfits" ]
    then
        SET_SRCDIR=/n/holylfs05/LABS/bhi/Lab/doeleman_lab/archive/2021March/extracted && SET_CORRDAT="Rev1-Cal:Rev1-Sci" && source bin/0.launch -f 230 -t eht
        source bin/1.version
        source bin/2.link #-m # for mixedpol
        source bin/3.fourfit
        source bin/4.alists
        source bin/5.check
        source bin/6.summary
    fi

    if [ $stage == "1.+flags+wins" ]
    then
        source bin/7.pcal
    fi

    if [ $stage == "2.+pcal" ]
    then
        source bin/7.adhoc
    fi

    if [ $stage == "3.+adhoc" ]
    then
        source bin/7.delays # -m # for mixedpol
    fi

    if [ $stage == "4.+delays" ]
    then
        source bin/7.close
    fi

    if [ $stage == "6.uvfits" ]
    then
	SET_EHTIMPATH="/n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/src/eht-imaging" && SET_SRCDIR=/n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/eht2021mixedpol/calibrate/230GHz/2021-april/dev-template/hops-b1/5.+close/data && SET_CORRDAT="Rev1-Cal:Rev1-Sci" && source bin/0.launch
        source bin/1.convert
        source bin/2.import
        python bin/3.average
    fi

    if [ $stage != "6.uvfits" ]
    then
        source bin/9.next
    fi

    cd ..
    echo "cd up to $(pwd)"
    echo "Finished stage $stage..."
done
