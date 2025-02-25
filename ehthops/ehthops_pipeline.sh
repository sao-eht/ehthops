#!/usr/bin/env bash
# To process band "bx", run from within one of the hops-bx directories
# Ensure that the correct python environment and the HOPS environment are activated before running this script

OPTIND=1 # so that getopts can pick up the arguments when the script is 'source'd

# Function to display help message
show_help() {
    echo "Usage: source $(basename "${BASH_SOURCE[0]}") [options]"
    echo
    echo "Command-line options:"
    echo "====================="
    echo "  -c <config>     Configuration file"
    echo "  -h, --help      Display this help message and exit"
    echo
    echo "Example:"
    echo "  source ehthops_pipeline.sh -c settings.config"
}

# Parse command-line arguments
while getopts "c:h" opt; do
        case $opt in
                c)
                        CONFIG=$OPTARG
                        ;;
                h|help)
                        show_help
                        return 0
                        ;;
                \?)
                        echo "Invalid option: -$OPTARG" >&2
                        show_help
                        return 1
                        ;;
                :)
                        echo "Option -$OPTARG requires an argument." >&2
                        show_help
                        return 1
            ;;
        esac
done

if [ -z "$CONFIG" ]; then
    echo "Error: -c <config> is a mandatory option." >&2
    show_help
    return 1
fi

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
done < "$CONFIG"

# Print the config array
for key in "${!config[@]}"; do
    echo "$key=${config[$key]}"
done

# Convert the stages string to an array
IFS=' ' read -r -a stages <<< "${config[stages]}"

# Working directory name
workdir=$(pwd)

# Loop through stages
for stage in ${stages[@]};
do
    echo "Starting stage $stage..."
    cd $stage
    echo "cd into $(pwd)"

    # Run fourfit for stages 0-5
    if [ $stage != "6.uvfits" ]
    then
        SET_SRCDIR="${config[ASSIGN_SRCDIR]}" && SET_CORRDAT="${config[ASSIGN_CORRDAT]}" && SET_METADIR="${config[ASSIGN_METADIR]}" && source bin/0.launch -y "${config[LAUNCH_YEAR]}" -d "${config[LAUNCH_DEPTH]}" -p "${config[LAUNCH_PATTERN]}"
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
        SET_SRCDIR="$workdir/5.+close/data" && SET_METADIR="${config[ASSIGN_METADIR]}" && source bin/0.launch -c "${config[LAUNCH_CAMPAIGN]}"
        source bin/1.convert
        source bin/2.import
        python bin/3.average
    fi

    # For stages 0-5, copy control files to the next stage
    if [ $stage != "6.uvfits" ]
    then
        source bin/9.next
    fi

    cd ..
    echo "cd up to $(pwd)"
    echo "Finished stage $stage..."
done