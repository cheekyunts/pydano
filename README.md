# pydano
Python scripts to do miniting and perform transactions and minting.



Connecting to remote cardano node instead of starting node on your laptop.
==========================================================================

1. Grab the latest cardano binary from [Download Link](https://developers.cardano.org/docs/get-started/installing-cardano-node)
2. Extract `cardano-cli` locally by extracting the downloaded package. `tar xzfv cardano-node-1.29.0-linux.tar.gz`
3. Install `cardano-*` binaries on local path. ` cp cardano-* $HOME/.local/bin/`
4. Start socat on your server, where actual node is running. `nohup socat TCP-LISTEN:8080,fork,reuseaddr, UNIX-CONNECT:$CARDANO_NODE_SOCKET_PATH&`
5. Start socat on your local machine, to connect to socket on remote node. `socat UNIX-LISTEN:node.socket,fork,reuseaddr,unlink-early, TCP:52.63.196.75:8080`
6. Export the path of `pwd/node.socket` as `CARDANO_NODE_SOCKET_PATH`

We are using 8080 port for communication between our remote node and local node here. Make sure:
1. 8080 port is open on remote host.
2. `echo $CARDANO_NODE_SOCKET_PATH` points to the correct location of socket

P.S: refer to the `./scripts/run_socat.sh` to starting socat locally.


Sending ADA from one wallet to other wallet
===========================================

```
python scripts/run_transactions.py --input_address addr_test1vqe6pyeqq66nffkku7ra8xhss97nzltclgnhn20u7xyhzwcu5zzvt --pay addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp=1000000 --signing_key keys/payment2.skey
```

This would send ADA as listed in `--pay` argument from wallet in `--input_address`.


Minting some Tokens
===================

```
python run_mint.py --input_address addr_test1vqe6pyeqq66nffkku7ra8xhss97nzltclgnhn20u7xyhzwcu5zzvt --pay addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp=ttestcheekyunts18 addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp=cheekyunttest12 addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp=cheekyunttest11 addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp=cheekyunttest10 --signing_key keys/payment2.skey --minting_script data/policy.script --log_level DEBUG --minting_lovlace 1758582
```

This can mint multiple tokens at once and doesn't require us to pay blanket 2ADA per minting.
