#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PARADEV_ROOT="$(cd "${PROJECT_ROOT}/../.." && pwd)"
ROOT="$(cd "${PARADEV_ROOT:-${DEFAULT_PARADEV_ROOT}}" && pwd)"
PARADEV_CONFIG_ROOT_OVERRIDE="${PARADEV_CONFIG_ROOT:-}"
PIHC3_MOD_ROOT="${PIHC3_MOD_ROOT:-${HOME}/Documents/Paradox Interactive/Hearts of Iron IV/mod}"
if [[ "${PIHC3_MOD_ROOT}" != /* ]]; then
    echo "PIHC3_MOD_ROOT must be an absolute path: ${PIHC3_MOD_ROOT}" >&2
    exit 2
fi
PIHC3_OUTPUT_ROOT="${PIHC3_MOD_ROOT}/PIHC3"
export PARADEV_HOI4_MOD_ROOT="${PIHC3_MOD_ROOT}"
if [[ ! -f "${ROOT}/scripts/_env.bash" ]]; then
    echo "ParaDev repository does not contain scripts/_env.bash: ${ROOT}" >&2
    exit 1
fi
cd "${ROOT}"
source "${ROOT}/scripts/_env.bash"
if [[ -n "${PARADEV_CONFIG_ROOT_OVERRIDE}" ]]; then
    export PARADEV_ROOT="${PARADEV_CONFIG_ROOT_OVERRIDE}"
else
    unset PARADEV_ROOT
fi
export PYTHONDONTWRITEBYTECODE=1

usage() {
    cat <<'USAGE'
Usage: bash compile.bash [--clean] [--clean-only] [--summary] [--plan-only] [--json] [--strict-metadata] [--profile PROFILE] [--family FAMILY] [--module MODULE] [--collection COLLECTION] [-- EXTRA_ARGS...]

Build the PIHC3 ParaDev project through the current CLI surface.

Options:
  --clean            Remove generated PIHC3 runtime directories and bytecode caches before building.
  --clean-only       Remove generated PIHC3 runtime directories and bytecode caches, then exit.
  --summary          Run the requested build and print only its compact summary.
  --plan-only        Run a dry build plan without writing artifacts or manifests.
  --json            Render the CLI build result as JSON.
  --strict-metadata Treat unknown module metadata keys as blocking diagnostics.
  --profile PROFILE Override the build profile.
  --family FAMILY   Build only one registered module or collection family.
  --module MODULE   Build one module. With --family, a bare object id is enough.
  --collection ID   Build one collection, optionally qualified by --family.

Artifact-emitting --family, --module, and --collection selectors keep their
requested compilation target. ParaDev automatically expands publication to the
project-wide localization closure required for deterministic PIHC3 output.
Compilation publishes project artifacts only and does not read or update the
external HoI4 launcher descriptor.

PARADEV_ROOT selects the ParaDev source checkout only. It is removed before the
CLI starts so it cannot redirect ParaDev configuration into that checkout. Set
PARADEV_CONFIG_ROOT explicitly only when an isolated configuration root is wanted.
USAGE
}

CLEAN=0
CLEAN_ONLY=0
SUMMARY=0
EMIT_ARTIFACTS=1
EMIT_MANIFESTS=1
EXTRA_ARGS=()

clean_generated_outputs() {
    rm -rf -- \
        "${PROJECT_ROOT}/.paradev" \
        "${PROJECT_ROOT}/build"
    mkdir -p -- "${PIHC3_OUTPUT_ROOT}"
    find "${PIHC3_OUTPUT_ROOT}" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
    find "${PROJECT_ROOT}" -path "${PROJECT_ROOT}/.git" -prune -o -type d -name __pycache__ -prune -exec rm -rf -- {} +
    find "${PROJECT_ROOT}" -path "${PROJECT_ROOT}/.git" -prune -o -type f -name '*.pyc' -delete
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clean)
            CLEAN=1
            shift
            ;;
        --clean-only)
            CLEAN=1
            CLEAN_ONLY=1
            shift
            ;;
        --summary)
            SUMMARY=1
            shift
            ;;
        --plan-only)
            EMIT_ARTIFACTS=0
            EMIT_MANIFESTS=0
            shift
            ;;
        --json|--strict-metadata)
            EXTRA_ARGS+=("$1")
            shift
            ;;
        --profile)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for --profile" >&2
                exit 2
            fi
            EXTRA_ARGS+=("$1" "$2")
            shift 2
            ;;
        --family|--module|--module-id|--collection|--collection-id)
            if [[ $# -lt 2 ]]; then
                echo "Missing value for $1" >&2
                exit 2
            fi
            EXTRA_ARGS+=("$1" "$2")
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        --)
            shift
            while [[ $# -gt 0 ]]; do
                EXTRA_ARGS+=("$1")
                shift
            done
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ "${CLEAN_ONLY}" == "1" ]]; then
    if [[ "${SUMMARY}" == "1" || "${EMIT_ARTIFACTS}" == "0" || $(array_len EXTRA_ARGS) -gt 0 ]]; then
        echo "--clean-only cannot be combined with build, summary, plan, or forwarded CLI options" >&2
        exit 2
    fi
fi

if [[ "${CLEAN}" == "1" ]]; then
    clean_generated_outputs
fi

if [[ "${CLEAN_ONLY}" == "1" ]]; then
    exit 0
fi

resolve_uv
uv_run python "${PROJECT_ROOT}/scripts/check_source_layout.py" --quiet
CMD=(uv_run paradev build "${PROJECT_ROOT}")
if [[ "${EMIT_ARTIFACTS}" == "1" ]]; then
    CMD+=(--emit-artifacts --no-sync-launcher-descriptor)
fi
if [[ "${EMIT_MANIFESTS}" == "1" ]]; then
    CMD+=(--emit-manifests)
fi
if [[ "${SUMMARY}" == "1" ]]; then
    CMD+=(--summary)
fi
if [[ $(array_len EXTRA_ARGS) -gt 0 ]]; then
    CMD+=("${EXTRA_ARGS[@]}")
fi
"${CMD[@]}"
