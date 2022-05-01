def hexstr(name):
    output = ''
    for n in name:
        output += hex(ord(n))[2:]
    return output
