# chia-scripts
## List of Scripts
`farmStats.sh`\
Basic harvester performance\
`getTransactions.sh`\
Using the RPC server, export transactions from a wallet to a csv file.\
`tail.sh`\
Tails the logs for harvester activity, adjusted display order and colors.

### farmStats.sh
In a command line, run `./farmStats.sh` to automatically parse the latest log file.\
If your logs are not in the default home directory location, edit the `logFile` path.

To use in Windows as-is, install https://git-scm.com/download/win

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

### tail.sh
In a command line, run `./tail.sh <coin name>` to start tailing the logs for chia or any fork.\
The `<coin name>` will need to be the same as the root directory for the coin's log path. For \
chia, the root path is `~/.chia` so the command to tail the chia logs is `./tail.sh chia`.
The default coloring is set at anything under 0.5s lookup green, 0.5s to 1s orange/yellow, and/
over 1s is red. Adjust these times by changing what `$16` is greater than in the script.
