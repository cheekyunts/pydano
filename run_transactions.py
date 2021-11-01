# coding: utf-8
import os
os.environ['CARDANO_NODE_SOCKET_PATH'] = '/home/gaurav/Documents/crypto/pydano/node.socket'
from pydano.transaction.transaction import TransactionConfig, BuildTransaction, SignTransaction, SubmitTransaction
tc = TransactionConfig("addr_test1vqe6pyeqq66nffkku7ra8xhss97nzltclgnhn20u7xyhzwcu5zzvt")
tc.add_tx_in("649940fab079859666a4b92d954382720f0a82473d00d9b2a1d6547f0816e942", 0)
tc.add_tx_out("addr_test1vryhvhqh89npuqr355tvdull9u8u4rj3vgvkmdmgklldzgsyvgrms", "lovelace", 1000000)
cct = BuildTransaction(tc)
cct.run_transaction()
st = SignTransaction(cct, "keys/payment2.skey")
st.run_transaction()
st = SubmitTransaction(st)
st.run_transaction()
