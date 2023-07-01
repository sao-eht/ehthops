# To be run from within 'hops-bx' directories
# set up envs
source /home/swc/env/ehthops324.sh

# list stages to be executed
stages=("0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close" "6.uvfits")

# loop through each stage
for stage in ${stages[@]}
do
    echo "Starting stage $stage..."
    cd $stage
    pwd

    # run fourfit for stages 0-5
    if [ $stage != "6.uvfits" ]
    then
        SET_SRCDIR=/data/2021-april/ce/2023_summer/data/raw/mk4 && SET_CORRDAT="Rev1-Cal" && source bin/0.launch
        source bin/1.version
        source bin/2.link
        source bin/3.fourfit
        source bin/4.alists
        source bin/5.check
        source bin/6.summary
    fi

    # run stage-specific scripts to generate control file information for the next stage
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
        source bin/7.delays
    fi

    if [ $stage == "4.+delays" ]
    then
        source bin/7.close
    fi

    # run stage 6; the calibration stage finishes with stage 5
    if [ $stage == "6.uvfits" ]
    then
	SET_EHTIMPATH="/home/swc/github/eht-imaging" && SET_SRCDIR=/home/iniyan/2021-hops-calibration/tutorial-25jun/2021-april/dev-template/hops-b4/5.+close/data && SET_CORRDAT="Rev1-Cal" && source bin/0.launch
        source bin/1.convert
        source bin/2.import
        python bin/3.average
    fi

    # for stages 0-5, copy control files to the next stage
    if [ $stage != "6.uvfits" ]
    then
        source bin/9.next
    fi

    cd ..
    echo "Finished stage $stage..."
done
