# set up envs
source $HOME/.bashrc
mamba activate ehthops310
source /n/holylfs05/LABS/bhi/Lab/doeleman_lab/inatarajan/software/installed/hops-3.24/bin/hops.bash

stages=("7.+apriori") # , "8.+polcal", "9.+netcal")

# working directory name
workdir=$(pwd)

for stage in ${stages[@]}
do
    echo "Starting stage $stage..."
    cd $stage
    echo "cd into $(pwd)"

    source bin/0.launch -f 230 -t eht -y 2021

    if [ $stage == "7.+apriori" ]
    then
        source bin/1.apriori
	source bin/2.import
        python bin/3.average
    fi

    cd ..
    echo "cd up to $(pwd)"
    echo "Finished stage $stage..."
done
