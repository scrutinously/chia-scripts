#!/usr/bin/bash
COIN=$1

tail -F ~/.$COIN/mainnet/log/debug.log | awk -v coin=$COIN -v red="$(tput setaf 1)" -v yellow="$(tput setaf 3)" -v green="$(tput setaf 2)" -v reset="$(tput sgr0)" \
'/proofs/ {
    if ($16>1) color=red; else if ($16>0.5) color=yellow; else color=green
    printf "%s%s %s  %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n",coin,": ",$1,$5,$6,$8, color,"|",$15,$16,$17, reset,$18,$19,$20,$13,$14
}'
