#!/usr/bin/bash
logFile="$HOME/.chia/mainnet/log/debug.log"
eligible=( $(awk '/plots were/ {printf "%d %s %s/\n",$5,$6,$8}' $logFile | sort -n | uniq -c) )
lookup=( $(awk '/plots were/ {printf "%f/\n",$16}' $logFile) )
total=$(echo ${eligible[@]} | awk 'BEGIN {RS = "/"}; {sum+=$1} END {print sum}')

now=$(date +%T)
today=$(date +%F)
past24=$(date +%F -d "yesterday")
if [ -f ${logFile}.1 ]; then
	subslots=$(cat ${logFile}.1 ${logFile} |\
	awk -v now=$now -v today=$today -v past24=$past24 '{FS="T"}; {if ($1 ~ today || $1 ~ past24 && $2 >= now) {print}}'|\
	awk '/64\/64/ {print}' | wc -l)
	if [ ${subslots} > 141 ]; then
		printf "Completed SubSlots (24h): \033[32m%5d\033[37m\n" $subslots
	else
		printf "Completed SubSlots (24h): \033[33m%5d\033[37m\n" $subslots
	fi
else
	echo "Harvester Stats:"
fi
echo ${eligible[@]} | awk -v "t=$total" 'BEGIN {RS = "/"}; {av=$1/t*100} {if ($1 != "") printf "%-3d %s %s: %8d | %.2f%\n",$2,$3,$4,$1,av}'
echo ${lookup[@]} | awk 'BEGIN {RS = "/"}; $1>0.5{c1++}; $1>1{c2++}; $1>5{c3++}; {l="Lookups Longer Than"};
        {sum+=$1}; END {printf "%-22s %5d\n%-22s %5d\n%-22s %5d\n%-22s %9f %s\n",l" 0.5s:",c1,"\033[33m"l" 1.0s:",c2,"\033[31m"l" 5.0s:",c3,"\033[37mAverage Lookup:",sum / NR,"sec"}'
echo ${lookup[@]} | awk 'BEGIN {RS = "/"}; $1>max{max=$1}; END {printf "%-16s %10f %s\n","Longest Lookup:",max,"sec"}'
echo "------------Warning------------"
awk '/WARNING/ {if ($7 ~ /handshake/ || $11 ~ /peername/ || $7 ~ /104/ || $7 ~ /32/ || $10 ~ /transport/ || $6 ~ /Incompatible/ || $6 ~ /Banning/) i++ c++;
        else if ($5 ~ /Block/) if ($8 > 4) lbv++ bv++ c++;else bv++ c++; else c++}; # I check for block validation time >4s to know when to vacuum my DB
        END {printf "%s%15d\n%s%4d\n%s%14d\n%s%11d\n","Total Warnings: ",c,"Block Validation Warnings: ",bv,"Validation > 4s: ",lbv,"Ignorable Warnings: ",i}' $logFile
echo "-------------Error-------------"
awk '/ERROR/ {if (/pooling/) p++ c++; else {c++}}; END {printf "%s%17d\n%s%15d\n","Total Errors: ",c,"Pooling Errors: ",p}' $logFile
