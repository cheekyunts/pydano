dir=$(pwd)
mkdir -p $dir/testnet/
mkdir -p $dir/mainet/
echo $dir/testnet/node.socket
echo $dir/mainnet/node.socket
export CARDANO_NODE_SOCKET_PATH=$dir/testnet/node.socket
socat UNIX-LISTEN:$dir/testnet/node.socket,fork,reuseaddr,unlink-early, TCP:172.31.30.193:8080&
socat UNIX-LISTEN:$dir/mainnet/node.socket,fork,reuseaddr,unlink-early, TCP:172.31.30.193:80&
disown %1
disown %2
