import os
import tempfile
import uuid

tempdir = tempfile.TemporaryDirectory()


def get_temp_file(prefix=""):
    file_name = str(uuid.uuid4())
    if prefix:
        file_name += f".{prefix}"
    return os.path.join(tempdir.name, file_name)


def protocol_params_file():
    return tempdir.name + "protocol_params.json"
