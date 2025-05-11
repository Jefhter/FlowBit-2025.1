import subprocess
import os

def _get_machine_id_wmi():
    return subprocess.run(
        [
            os.path.normpath(
                os.path.join(os.path.dirname(os.environ.get("comspec")), "wbem", "wmic.exe")
            ),
            "csproduct",
            "get",
            "UUID",
        ],
        stdout=subprocess.PIPE,
        shell=True,
    )

def _get_machine_id_powershell():
    return subprocess.run(
        [
            "powershell", 
            "-Command", 
            "Get-CimInstance -ClassName Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
        ],
        stdout=subprocess.PIPE,
        shell=True,
    )

def get_machine_id():
    machine_id = _get_machine_id_wmi()
    if machine_id.returncode != 0:
        machine_id = _get_machine_id_powershell()

    return sorted(
        machine_id.stdout.splitlines(),
        key=lambda x: len(x),
    )[-1].strip()




