# Skript, ktorý z externého úložiska (smb://)
# a. Vypíše všetky prázdne zložky. K nim napíše flag "EMPTY".
# b. Vypíše všetky súbory, ktoré sú väčšie ako 500MB. K nim napíše flag "EXCEEDED"
# c. Zoradí výstup abecedne podľa "Flag"
# Formát: .csv
# Stĺpce: "Path" - celá cesta; "Name" - názov foldru alebo súboru; "Flag" - empty/exceeded

from getpass import getpass

import pandas as pd
from smbclient import listdir, register_session, scandir
from smbprotocol import exceptions as smbex

server = "192.168.16.100"
root = r"\\192.168.16.100\SMB"
size_limit = 500 * 1024 * 1024  # convert to bytes

username = input("username: ")
password = getpass("password: ")

data = []


def smbwalk(path: str):
    """Recursively walks through SMB share.
    
    :param path: Path to walk.""" 
    for file_info in scandir(path):
        if file_info.is_file():
            if file_info.stat().st_size > size_limit:
                data.append(
                    {
                        "Path": file_info.path,
                        "Name": file_info.name,
                        "Flag": "EXCEEDED",
                    }
                )
        elif file_info.is_dir():
            if not listdir(file_info.path):
                data.append(
                    {
                        "Path": file_info.path,
                        "Name": file_info.name,
                        "Flag": "EMPTY",
                    }
                )
            else:
                smbwalk(file_info.path)
        else:
            pass


try:
    register_session(server, username=username, password=password)
    smbwalk(root) # start walking with "root" as a path
    df = pd.DataFrame(data)
    df = df.sort_values(by="Flag")
    df.to_csv("output.csv", index=False)

except smbex.LogonFailure:
    print("Wrong credentials")
except ValueError as e:
    if e.__cause__ and isinstance(e.__cause__, TimeoutError):
        print("Server not found")
except smbex.BadNetworkName:
    print("Wrong root path")
