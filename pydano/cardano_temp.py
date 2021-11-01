import tempfile

tempdir = tempfile.TemporaryDirectory()

def protocol_params_file():
    return tempdir.name + 'protocol_params.json'

