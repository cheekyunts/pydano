# coding: utf-8
import os
os.environ['CARDANO_NODE_SOCKET_PATH'] = '/home/gaurav/Documents/crypto/pydano/node.socket'
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction
in_address = "addr_test1vqe6pyeqq66nffkku7ra8xhss97nzltclgnhn20u7xyhzwcu5zzvt"


tc = TransactionConfig(in_address)
tc.add_input_utxos(in_address)
tc.add_tx_out("addr_test1vryhvhqh89npuqr355tvdull9u8u4rj3vgvkmdmgklldzgsyvgrms", "lovelace", 1000000)
tc.add_tx_out("addr_test1vqjx7cmy52973y868fvesd7tjuvj9njxqgzen5vyvs9cw0qqpcqjp", "lovelace", 1000000)


print("Building Transaction")
cct = BuildTransaction(tc)
cct.run_transaction()
print("Signing Transaction")
st = SignTransaction(cct, "keys/payment2.skey")
st.run_transaction()
print("Submitting Transaction")
st = SubmitTransaction(st)
st.run_transaction()
