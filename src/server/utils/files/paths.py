from pathlib import Path
from typing import Union

class UnsafePathException(Exception):
    """Exception raised for unsafe paths."""
    pass
 
def join_paths(
    *paths: Union[str, Path], 
    check: bool = False, 
    mkdir: bool = False,
    eafp: bool = False
) -> Path:
    """
    Joins multiple paths into a single absolute path 

    Args:
        *paths (Union[str, Path]): One or more paths to join together. The first path 
            is considered the "base directory," and the resulting path must remain within 
            this directory for security reasons.
        check (bool, optional): If `True`, the function checks if the resolved path exists, 
            raising a `FileNotFoundError` if it does not. Defaults to `False`.
        mkdir (bool, optional): If `True`, the function creates the parent directories 
            of the resolved path if they do not exist, using `Path.mkdir()`.
        EAFP (bool, optional): easier to ask forgiveness than permission

    Returns:
        Path: The fully joined and resolved path as a `Path` object.

    Raises:
        ValueError: If no paths are provided.
        UnsafePathException: If the resulting path is outside the base directory.
        FileNotFoundError: If `check` is `True` and the path does not exist.

    Note:
        This function ensures that the final path is within the base directory for security 
        reasons. This can help prevent issues like directory traversal attacks when handling 
        file paths dynamically.
    """

    if len(paths) < 1:
        raise ValueError("At least one path must be provided.")

    paths = [Path(p) if isinstance(p, str) else p for p in paths]
    base_dir = paths[0].resolve()

    full_path = base_dir
    for p in paths[1:]:
        full_path = full_path / p

    resolved_path = full_path.resolve()

    if not resolved_path.is_relative_to(base_dir):
        raise UnsafePathException(f"The path {resolved_path} is outside the safe directory {base_dir}.")

    if check and not resolved_path.exists():
        raise FileNotFoundError(f"The path {resolved_path} does not exist")

    elif mkdir and (not eafp or resolved_path.parent.exists()):
        resolved_path.parent.mkdir(parents=True, exist_ok=True)

    return resolved_path




