Pydano is an open-source library, which allows the developer to add Cardano transactions, receiving payments, CNFT minting to their application with ease.

Interacting with the Cardano blockchain requires using `cardano_cli`, which involves manually setting up the transactions. Motivation for writing the Pydano was to:

* Allow developers to write Cardano application with ease of python, without worrying too much about underlying `cardano_cli` interactions.
* Remove the burden of doing repetitive tasks such as querying protocol parameters, finding the input UTXOs for the transaction.
* Have a reproducible way to build and execute transactions from python.


Building and executing a transaction from `cardano_cli` requires five steps:

1. Query the protocol parameters.
2. Query and find the relevant UTXOs based on `input_address`.
3. Build the transaction using input UTXOs, protocol parameters, out payment addresses.
4. Sign the transaction using your signing key.
5. Submit the transaction to the Cardano network.

The library aims to hide the complexity, by managing the information flow between these steps. The library expects only `input_address`, `out address`, `signing key`.
