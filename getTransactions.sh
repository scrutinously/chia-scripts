#!/usr/bin/bash
read -p "Output CSV Filename:`echo $'\n > '`" csv
read -p "Print by:`echo $'\n '`(1)Number of most recent transactions`echo $'\n '`(2)To/From block height`echo $'\n > '`" input
if [[ $input -eq 1 ]]
then
        read -p "Enter number of most recent transactions:`echo $'\n > '`" end
        start=0
        data='{"wallet_id": 1, "start": '$start', "end": '$end'}'

curl -s -X POST \
--insecure --cert ~/.chia/mainnet/config/ssl/wallet/private_wallet.crt --key ~/.chia/mainnet/config/ssl/wallet/private_wallet.key \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
'https://localhost:9256/get_transactions' \
-d "$data" | python -m json.tool | \
sed 's/"//g;/],$/d;/{$/d;/}$/d;s/,//g' | \
awk 'BEGIN {RS = "additions: [[]\n"} {records[i++]=$0}; \
END {RS = "\n"} {for (i in records) \
{if ($1!~/amount/) print "TX," "Height," "Amount," "Address"; else {if (/sent: 1/) tx="sent"; else tx="rec"} \
{for (a=1;a<=NF;a++) {if ($a~/^confirmed:/) am=$(a-1); else if ($a~/height/) bl=$(a+1); else if ($a~/to_address/) ad=$(a+1)} \
{printf "%s,%s,%s,%s\n",tx,bl,am,ad}}}}' | \
sed '/^,,/d' > $csv

elif [[ $input -eq 2 ]]
then
        read -p "Enter starting block height:`echo $'\n > '`" fromBlock
        read -p "Enter ending block height:`echo $'\n > '`" toBlock
        start=0
        end=100000
        data='{"wallet_id": 1, "start": '$start', "end": '$end'}'

curl -s -X POST \
--insecure --cert ~/.chia/mainnet/config/ssl/wallet/private_wallet.crt --key ~/.chia/mainnet/config/ssl/wallet/private_wallet.key \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
'https://localhost:9256/get_transactions' \
-d "$data" | python -m json.tool | \
sed 's/"//g;/],$/d;/{$/d;/}$/d;s/,//g' | \
awk -v fromBlock=$fromBlock -v toBlock=$toBlock 'BEGIN {RS = "additions: [[]\n"} {records[i++]=$0}; \
END {RS = "\n"} {for (i in records) \
{if ($1!~/amount/) print "TX," "Height," "Amount," "Address"; else {if (/sent: 1/) tx="sent"; else tx="rec"} \
{for (a=1;a<=NF;a++) {if ($a~/^confirmed:/) am=$(a-1); else if ($a~/height/) bl=$(a+1); else if ($a~/to_address/) ad=$(a+1)} \
{if (bl>=fromBlock && bl<=toBlock) printf "%s,%s,%s,%s\n",tx,bl,am,ad}}}}' | \
sed '/^,,/d' > $csv

else
        echo "Not a valid response"
fi

