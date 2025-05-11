import platform

__all__ = ['os_is_windows', 'os_is_linux']

def os_is_windows() -> bool:
    return platform.system() == 'Windows'

def os_is_linux() -> bool:
    return platform.system() == 'Linux'




