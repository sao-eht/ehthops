#!/usr/bin/env bash
# To process band "bx", run from within one of the hops-bx directories
# Ensure that the correct python environment and the HOPS environment are activated before running this script

# Function to display help message
show_help() {
    echo "Usage: source $(basename "${BASH_SOURCE[0]}") <config>"
    echo
    echo "Positional arguments:"
    echo "====================="
    echo "  <config>         Configuration file"
    echo
    echo "Example:"
    echo "  source ehthops_pipeline.sh settings.config"
}

# Check for help argument
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
    return 0
fi

# Check for the configuration file argument
if [ -z "$1" ]; then
    echo "Error: <config> is a mandatory argument." >&2
    show_help
    return 1
fi

CONFIGFILE=$1

# Unset config variable if it exists and declare it as an associative array
unset config
declare -A config

# read all key value pairs separated by '=' from the config file
# and store them in the config associative array
while IFS='=' read -r key value || [ -n "$key" ]; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue

    # Remove leading and trailing whitespace
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Store the key-value pair in the config array
    config["$key"]="$value"
done < "$CONFIGFILE"

# Print the config array
for key in "${!config[@]}"; do
    echo "$key=${config[$key]}"
done

# Convert the stages string to an array
IFS=' ' read -r -a stages <<< "${config[stages]}"

# Working directory name
workdir=$(pwd)

# Check if the first stage is "1.+flags+wins" and ensure
# some steps from 0.bootstrap is run regardless
if [[ "${stages[0]}" == "1.+flags+wins" ]]; then
    echo "Stage 0.boostrap not requested. Running only 0.bootstrap setup..."
    cd 0.bootstrap
    SET_SRCDIR="${config[SET_SRCDIR]}" && SET_CORRDAT="${config[SET_CORRDAT]}" && SET_METADIR="${config[SET_METADIR]}" && SET_OBSYEAR="${config[SET_YEAR]}" && SET_MIXEDPOL="${config[SET_MIXEDPOL]}" && SET_HAXP="${config[SET_HAXP]}" && source bin/0.launch
    source bin/9.next
    cd ..
fi

# Loop through stages
for stage in ${stages[@]};
do

    echo "Starting stage $stage..."
    cd $stage
    echo "cd into $(pwd)"

    # Run fourfit for stages 0-5
    if [[ $stage =~ ^[0-5] ]]
    then
        SET_SRCDIR="${config[SET_SRCDIR]}" && SET_CORRDAT="${config[SET_CORRDAT]}" && SET_METADIR="${config[SET_METADIR]}" && SET_OBSYEAR="${config[SET_YEAR]}" && SET_MIXEDPOL="${config[SET_MIXEDPOL]}" && SET_HAXP="${config[SET_HAXP]}" && source bin/0.launch
        source bin/1.version
        source bin/2.link
        source bin/3.fourfit
        source bin/4.alists
        source bin/5.check
        source bin/6.summary
    fi

    # Run stage-specific scripts to generate control file information for the next stage
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

    # Run stage 6 after the 5 fringe-fitting stages; SRCDIR is now 5.+close/data
    if [ $stage == "6.uvfits" ]
    then
        SET_EHTIMPATH="${config[SET_EHTIMPATH]}" && SET_SRCDIR="$workdir/5.+close/data" && SET_METADIR="${config[SET_METADIR]}" && SET_CAMPAIGN="${config[SET_CAMPAIGN]}" && source bin/0.launch
        source bin/1.convert
        source bin/2.import
        python bin/3.average
    fi

    # Run stage 7 after the 6 uvfits stage; SRCDIR is now 6.uvfits
    if [ $stage == "7.+apriori" ]
    then
        SET_SRCDIR="$workdir/6.uvfits" && SET_METADIR="${config[SET_METADIR]}" && SET_OBSYEAR="${config[SET_YEAR]}" && source bin/0.launch
        source bin/1.antab2sefd
        source bin/2.applycal
        source bin/3.import
        python bin/4.average
    fi

    # copy control files and necessary scripts to the next stage
    if [ $stage != "7.+apriori" ]
    then
        source bin/9.next
    fi
    
    cd ..
    echo "cd up to $(pwd)"
    echo "Finished stage $stage..."
done
