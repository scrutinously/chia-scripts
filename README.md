# chia-scripts
## List of Scripts
`farmStats.sh`\
Basic harvester performance\
`getTransactions.sh`\
Using the RPC server, export transactions from a wallet to a csv file.

### farmStats.sh
In a command line, run `./farmStats.sh` to automatically parse the latest log file.\
To parse all of the existing log files in the mainnet/logs directory, change `debug.log`\
to `debug.log.*`.

### getTransactions.sh
In a command line, run `./getTransactions.sh` and follow the prompts:\
Entering 1 at the first prompt will prompt for a number of recent transactions to display\
(i.e. the last 20 transactions). Entering 2 at the first prompt will prompt for a starting\
block-height and an ending block-height to display transactions for, these do not need to\
be very accurate, for example, to display all transactions you could use 0 as the start\
and 3000000 as the end. In the script this is hard coded to 100,000 transactions, so if you\
have more than that, change the `end` parameter in the script.\

Currently there is a limitation in the API or possibly in the database that prevents the API\
from reporting send transactions from before approximately block-height 800000, which is\
approximately the time of the release of chia client 1.2.6.
