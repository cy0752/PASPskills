#!/bin/bash

WORKFLOW_DIR="${WORKFLOW_DIR:-/path/to/project}"
RUN_ID="${RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-seq_all}"
START_SAMPLE="${START_SAMPLE:-0}"
END_SAMPLE="${END_SAMPLE:-799}"
SHARED_RUN="${SHARED_RUN:-${WORKFLOW_DIR}/0.shared_basis/runs/<shared-run-id>}"

RUN_DIR="${WORKFLOW_DIR}/1.method6_template/runs/${RUN_ID}"
mkdir -p "${RUN_DIR}"
echo -e "sample_id\tstatus" > "${RUN_DIR}/status.tsv"

source /opt/intel/oneapi/setvars.sh
ulimit -s unlimited
export OMP_NUM_THREADS=1
export I_MPI_HYDRA_BOOTSTRAP=slurm
export I_MPI_FABRICS=shm:ofi
export I_MPI_OFI_PROVIDER=tcp
unset UCX_TLS
unset UCX_NET_DEVICES
export MKLROOT=/opt/intel/oneapi/mkl/latest
export I_MPI_ROOT=/opt/intel/oneapi/mpi/latest
export LD_LIBRARY_PATH=$MKLROOT/lib/intel64:$I_MPI_ROOT/lib/release:$I_MPI_ROOT/lib:$LD_LIBRARY_PATH
export PASP_MACHINE_ID_FILE=/data/secure/path/pasp_machine_id.dat

for i in $(seq "${START_SAMPLE}" "${END_SAMPLE}"); do
  SAMPLE_DIR="${RUN_DIR}/${i}"
  mkdir -p "${SAMPLE_DIR}"
  cp "${WORKFLOW_DIR}/1.method6_template/input/PASP.input" "${SAMPLE_DIR}/"
  cp "${WORKFLOW_DIR}/1.method6_template/input/cell.str" "${SAMPLE_DIR}/"
  cp "${WORKFLOW_DIR}/1.method6_template/input/unit_cell.str" "${SAMPLE_DIR}/"
  cp "${SHARED_RUN}/local_mode_PM.dat" "${SAMPLE_DIR}/"
  cp "${WORKFLOW_DIR}/path_b_inputs/${i}/distortion.pos" "${SAMPLE_DIR}/"
  if [ -f "${WORKFLOW_DIR}/path_b_inputs/${i}/distortion.MAGMOM" ]; then
    cp "${WORKFLOW_DIR}/path_b_inputs/${i}/distortion.MAGMOM" "${SAMPLE_DIR}/"
  fi
  cd "${SAMPLE_DIR}"
  /root/PASP/PASP.x > log.out 2>&1
  if grep -q "PASP is finished gracefully." log.out; then
    echo -e "${i}\tok" >> "${RUN_DIR}/status.tsv"
  else
    echo -e "${i}\tfailed" >> "${RUN_DIR}/status.tsv"
  fi
done
