# set up envs
source $HOME/.bashrc
mamba activate ehthops310
source /path/to/installed/hops/bin/hops.bash

stages=("7.+apriori") # , "8.+polcal", "9.+netcal")

# working directory name
workdir=$(pwd)
# extract band from working directory
band=$(echo $workdir | sed 's|.*/hops-\(..\)/\?.*$|\1|')

for stage in ${stages[@]}
do
    echo "Starting stage $stage..."
    cd $stage
    echo "cd into $(pwd)"

    if [ $stage == "7.+apriori" ]
    then
	    SET_EHTIMPATH="/path/to/eht-imaging" && SET_SRCDIR=$workdir/6.uvfits && SET_METADIR=/path/to/metadata && source bin/0.launch -c EHT2021
        source bin/1.apriori
        #source bin/2.import
        #python bin/3.average
    fi

    cd ..
    echo "cd up to $(pwd)"
    echo "Finished stage $stage..."
done
