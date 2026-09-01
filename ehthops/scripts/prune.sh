#!/usr/bin/env bash
# Prune the data/ directory produced during an ehthops data reduction.
#
# This script ONLY modifies the data/ directory inside each stage. At
# level 3, uvfits files in postproc stages are also deleted. No other
# directories are modified.
#
# Can either execute (./cleanup.sh -l LEVEL) or source in an interactive
# bash or zsh session (source cleanup.sh -l LEVEL or . cleanup.sh
# -l LEVEL). Sourcing also leaves cleanup_level_1/2/3 defined so that
# the individual cleanup functions can be called directly afterwards.

# Keep track of whether a dry run is being requested.
_ehc_dry_run=0

# Resolve name to be shown differently per shell because
# bash and zsh disagree on how $0/BASH_SOURCE behave when sourced.
if [ -n "${ZSH_VERSION:-}" ]; then
    _ehc_script_name=$(basename "${(%):-%N}")
else
    _ehc_script_name=$(basename "${BASH_SOURCE[0]:-$0}")
fi

_ehc_usage() {
    cat <<EOF
Usage: ${_ehc_script_name} -l LEVEL

Prune data products from an ehthops pipeline run based on LEVEL.

In every pruned data/ directory:
  * files directly under data/ are preserved
  * the directory structure under data/ is preserved
  * inside any subdirectory, only *.uvfits files are kept;
    all other files (including .dat under data/adhoc) are deleted

Note: 3.fourfit's per-scan/per-task fourfit logs are NOT under data/ -- they
are written to 0.bootstrap/log/fourfit/, which this script never touches
(it only ever modifies data/ directories).

Options:
  -l LEVEL   Cleanup level to perform (required). One of:
               1   Prune data/ for stages 0-4
               2   Prune data/ for stages 0-5
               3   Prune data/ for stages 0-5 AND remove unaveraged uvfits
                   files from postproc directories
  -n, --dry-run
             List every file that would be deleted.
  -h         Show this help message and exit

Examples:
  ${_ehc_script_name} -l 3
  ${_ehc_script_name} -l 3 -n      # preview level 3, delete nothing
EOF
}

# Prune the data/ directory of a single stage.
# Argument: the stage directory name.
_ehc_prune_data() {
    local stage="$1"
    local data_dir="$stage/data"

    if [ ! -d "$data_dir" ]; then
        return 0
    fi

    # In dry-run mode, print the matches instead of deleting them.
    local action="-delete"
    if [ "$_ehc_dry_run" -eq 1 ]; then
        action="-print"
        echo "[dry run] Would prune $data_dir:"
    else
        echo "Pruning $data_dir..."
    fi

    # General rule (everywhere under data/ EXCEPT the adhoc/ subtree):
    # delete every file that lives at least one level below data/ (i.e. inside
    # a subdirectory) and is not one of the preserved extensions. Files
    # directly under data/ are excluded via -mindepth 2. Directories are never
    # deleted, so the tree structure is preserved. The adhoc/ subtree is
    # excluded here via -path and handled separately below, because it follows
    # a different rule.
    #
    # *.out/*.err are no longer carved out here: 3.fourfit now logs to
    # log/fourfit/ instead of into data/ scan directories (so that a stray log
    # file can never be mistaken for a type-2 fringe file by downstream
    # filename-pattern-based tools, e.g. hops2uvfits.py), and nothing else
    # writes *.out/*.err under data/. If that ever changes, this rule will
    # delete them like any other non-uvfits file.
    find "$data_dir" -mindepth 2 \( -type f -o -type l \) \
        ! -path "$data_dir/adhoc/*" \
        ! -name '*.uvfits' \
        "$action"

    # under data/adhoc/, delete ONLY *.dat files and keep everything else.
    if [ -d "$data_dir/adhoc" ]; then
        find "$data_dir/adhoc" \( -type f -o -type l \) -name '*.dat' "$action"
    fi
}

# Remove unaveraged uvfits files.
# Argument: the stage directory name.
_ehc_prune_uvfits() {
    local stage="$1"

    if [ ! -d "$stage" ]; then
        return 0
    fi

    local action="-delete"
    if [ "$_ehc_dry_run" -eq 1 ]; then
        action="-print"
        echo "[dry run] Would remove non-averaged uvfits under $stage:"
    else
        echo "Removing non-averaged uvfits under $stage..."
    fi

    # Match *.uvfits within expt_no dirs, and keep only the averaged uvfits files.
    find "$stage" -type d -regextype posix-extended -regex '.*/[0-9]{4,5}' \
        -exec find {} \( -type f -o -type l \) -name '*.uvfits' ! -name '*+avg.uvfits' "$action" \;
}

cleanup_level_1() {
    local stage
    for stage in "0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays"; do
        _ehc_prune_data "$stage"
    done
}

cleanup_level_2() {
    local stage
    for stage in "0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close"; do
        _ehc_prune_data "$stage"
    done
}

cleanup_level_3() {
    local stage
    for stage in "0.bootstrap" "1.+flags+wins" "2.+pcal" "3.+adhoc" "4.+delays" "5.+close"; do
        _ehc_prune_data "$stage"
    done
    for stage in "6.uvfits" "7.+apriori" "8.+polcal"; do
        _ehc_prune_uvfits "$stage"
    done
}

_ehc_main() {
    local level=""
    local opt
    local OPTIND=1

    # Reset dry-run state each call so a previous invocation (when sourced)
    # cannot leak into this one.
    _ehc_dry_run=0

    # getopts handles only short options, so translate the --dry-run long form
    # to -n before parsing. Other args are passed through unchanged.
    local args=()
    local a
    for a in "$@"; do
        case "$a" in
            --dry-run) args+=("-n") ;;
            *) args+=("$a") ;;
        esac
    done
    set -- "${args[@]}"

    while getopts ":l:nh" opt; do
        case "$opt" in
            l) level="$OPTARG" ;;
            n) _ehc_dry_run=1 ;;
            h) _ehc_usage; return 0 ;;
            \?) echo "Unknown option: -$OPTARG" >&2; _ehc_usage; return 1 ;;
            :) echo "Option -$OPTARG requires an argument" >&2; _ehc_usage; return 1 ;;
        esac
    done

    if [ -z "$level" ]; then
        echo "Error: cleanup level is required (-l)." >&2
        _ehc_usage
        return 1
    fi

    case "$level" in
        1) cleanup_level_1 ;;
        2) cleanup_level_2 ;;
        3) cleanup_level_3 ;;
        *) echo "Error: invalid level '$level'. Must be 1, 2, or 3." >&2; _ehc_usage; return 1 ;;
    esac
}

_ehc_main "$@"

