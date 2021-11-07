# Before Installation setup

We need to setup a `node.socket` to communicate with cardano network and `cardano-cli` to use the library. Section below describe how to setup `cardano-cli` and `node.socket`.

TLDR: Refer `./scripts/setup_local.sh`

## Setting up communication with Cardano node

`cardano-cli` interact with Cardano node using `node.socket`. We need to configure this socket on our local machine to be able to use Pydano and do transactions. We can either run the Cardano node on a remote machine and just connect the sockets using the `socat` utility or point to the `node.socket` of your local installing.

### Installing `cardano-node` locally and point to node.socket.

Follow the Cardano tutorial to start and sync your node [Running your Cardano node](https://developers.cardano.org/docs/get-started/running-cardano/)

Remember the path of socket you provided in `--socket-path` argument. Use that to set the environment variable `export CARDANO_NODE_SOCKET_PATH=<PATH>`.

## Connect `node.socket` running on the remote machine to a local machine.

1. Start `socat` on your local machine, to connect to a socket on the remote node. 
`socat UNIX-LISTEN:node.socket,fork,reuseaddr,unlink-early, TCP:<IP_ADDR>:<PORT>` [Replace <IP_ADDR> with ip of your remote machine]
6. Export the path of `pwd/node.socket` as `CARDANO_NODE_SOCKET_PATH`

We are using the <PORT> for communication between our remote node and local node here. Make sure:
1. <PORT> port is open on the remote host.
2. `echo $CARDANO_NODE_SOCKET_PATH` points to the correct location of the socket


P.S: refer to the `./scripts/run_socat.sh` to starting socat locally.

We have an AWS node running both testnet and mainnet node, you can use that node if you don't want to sync up a node yourself.


## Installing `cardano-cli` locally
1. Grab the latest Cardano binary from [Download Link](https://developers.cardano.org/docs/get-started/installing-cardano-node)
2. Extract `cardano-cli` locally by extracting the downloaded package. `tar xzfv cardano-node-1.29.0-linux.tar.gz`
3. Install `cardano-*` binaries on local path. `cp cardano-* $HOME/.local/bin/`

Above steps can be found in the script `./scripts/setup_local.sh`

Pydano provides a library to add transactions to your application. It also provides a command line tool to do basic stuff like doing a transaction, mint a cnft.
