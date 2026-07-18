# lib/log.sh — shared logging library for ehthops.
# Sourced by 0.launch to provide a consistent logging interface.
# Contains only function definitions: no code executes at source time,
# so sourcing multiple times (once per stage via 0.launch) is harmless.
#
# Usage:
#   info    "message"
#   warning "message"
#   error   "message"
#
# Reads (set by 0.launch after WRKDIR is known):
#   LOG_FILE  path to the per-stage TSV event log
#             defaults to /dev/stderr so messages are never
#             silently lost if LOG_FILE is not yet set.
#   STAGE     current stage name, e.g. "1.+flags+wins";
#             defaults to "unknown" if not set.
#
# TSV columns (one record per log() call):
#   timestamp <TAB> level <TAB> stage <TAB> message

log() {
    local level="$1"; shift
    local msg="$*"
    local ts
    ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    # Human-readable line to stdout (visible in slurm-<jobid>.out)
    printf '%s [%s] %s\n' "$ts" "$level" "$msg"
    # Structured TSV record appended to the stage log file
    printf '%s\t%s\t%s\t%s\n' \
        "$ts" "$level" "${STAGE:-unknown}" "$msg" \
        >> "${LOG_FILE:-/dev/stderr}"
}

info()    { log INFO    "$@"; }
warning() { log WARNING "$@"; }
error()   { log ERROR   "$@"; }

step_start() {
    _STEP_T0=$(date +%s)
    info "BEGIN $1"
}

step_end() {
    local elapsed=$(( $(date +%s) - ${_STEP_T0:-0} ))
    info "END $1 (${elapsed}s)"
}
