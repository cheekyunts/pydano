rm -rf /tmp/tmp_pydano/
mkdir -p /tmp/tmp_pydano/
cd /tmp/tmp_pydano/
wget https://hydra.iohk.io/build/7408438/download/1/cardano-node-1.29.0-linux.tar.gz
tar xzfv cardano-node-1.29.0-linux.tar.gz
sudo mv cardano-* $HOME/.local/bin/
cd -
sudo apt-get install socat
dir=$(pwd)
mkdir -p $dir/testnet/
mkdir -p $dir/mainnet/
echo $dir/testnet/node.socket
echo $dir/mainnet/node.socket
export CARDANO_NODE_SOCKET_PATH=$dir/testnet/node.socket
socat UNIX-LISTEN:$dir/testnet/node.socket,fork,reuseaddr,unlink-early, TCP:52.63.196.75:8080&
socat UNIX-LISTEN:$dir/mainnet/node.socket,fork,reuseaddr,unlink-early, TCP:52.63.196.75:80&
disown %1
disown %2
