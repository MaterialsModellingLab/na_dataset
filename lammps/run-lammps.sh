#!/usr/bin/env bash

OMP_PROC_BIND=spread \
OMP_PLACES=threads \
    lmp -k on g 1 -sf kk "$@" >/dev/null

