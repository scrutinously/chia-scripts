#!/usr/bin/bash
logFile="$HOME/.chia/mainnet/log/debug.log"
eligible=( $(awk '/plots were/ {printf "%d %s %s/\n",$5,$6,$8}' $logFile | sort -n | uniq -c) )
lookup=( $(awk '/plots were/ {printf "%f/\n",$16}' $logFile) )
total=$(echo ${eligible[@]} | awk 'BEGIN {RS = "/"}; {sum+=$1} END {print sum}')


echo ${eligible[@]} | awk -v "t=$total" 'BEGIN {RS = "/"}; {av=$1/t*100} {if ($1 != "") printf "%-3d %s %s: %8d | %.2f%\n",$2,$3,$4,$1,av}'
echo ${lookup[@]} | awk 'BEGIN {RS = "/"}; $1>0.5{c1++}; $1>1{c2++}; 1>5{c3++}; {l="Lookups Longer Than"};
        {sum+=$1}; END {printf "%-22s %5d\n%-22s %5d\n%-22s %5d\n%-22s %9f %s\n",l" 0.5s:",c1,"\033[33m"l" 1.0s:",c2,"\033[31m"l" 5.0s:",c3,"\033[37mAverage Lookup:",sum / NR,"sec"}'
echo ${lookup[@]} | awk 'BEGIN {RS = "/"}; $1>max{max=$1}; END {printf "%-16s %10f %s\n","Longest Lookup:",max,"sec"}'
