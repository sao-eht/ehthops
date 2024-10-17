# To be run from within 'hops-bx' directories
# set up envs
source $HOME/.bashrc
mamba activate ehthops310 # activate the mamba environment with the necessary packages installed
source /path/to/hops.bash

# list of stages to run
stages=("0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close" "6.uvfits")

# working directory name
workdir=$(pwd)
# extract band from working directory
band=$(echo $workdir | sed 's|.*/hops-\(..\)/\?.*$|\1|')

for stage in ${stages[@]}
do
    echo "Starting stage $stage..."
    cd $stage
    echo "cd into $(pwd)"

    # run fourfit for stages 0-5
    if [ $stage != "6.uvfits" ]
    then
        SET_SRCDIR=/path/to/data/archive && SET_CORRDAT="Rev1-Cal:Rev1-Sci" && SET_METADIR=/path/to/metadata && source bin/0.launch -y 2021 -m -d 4 -p "e21f.*-$band-.*.hops/"
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

    # run stage 6 after the 5 fringe-fitting stages; SRCDIR is now 5.+close/data
    if [ $stage == "6.uvfits" ]
    then
	    SET_EHTIMPATH="/path/to/eht-imaging" && SET_SRCDIR=$workdir/5.+close/data && SET_METADIR=/path/to/metadata && source bin/0.launch -c EHT2021
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
    echo "cd up to $(pwd)"
    echo "Finished stage $stage..."
done
