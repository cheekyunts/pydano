dir=$(pwd)
echo $dir/node.socket
export CARDANO_NODE_SOCKET_PATH=$dir/node.socket
socat UNIX-LISTEN:node.socket,fork,reuseaddr,unlink-early, TCP:52.63.196.75:8080&
disown %1
