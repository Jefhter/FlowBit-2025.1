import asyncio
from pathlib import Path
import random
from typing import Callable, Any, Union, Tuple, List
from logging import Logger, getLogger

from.sessions import get_sessions_phones
from.client import Client, DELAY, FatalException
from..miscellaneous import sleep, is_list_like, Runner
from..files import read_csv
_base_loger = getLogger('Telethon')


async def run_client(
    session: Union[str, Path],
    phone: str,
    api_id: Union[str, int],
    api_hash: str,
    callback: Callable[[Client], Any],
    base_logger: Logger = _base_loger,
    delay: float = DELAY,
    receive_updates: bool = False,
    cancelled_event=None,
    check_spam: bool = False,
    **keyargs: Any
) -> None:
    """
    Runs the Telegram client and executes the callback function.

    Args:
        session (str): The session string or path to the session file.
        phone (str): The phone number associated with the session.
        api_id (int): The API ID for the Telegram client.
        api_hash (str): The API hash for the Telegram client.
        callback (Callable[[TelegramClient], Any]): The function to execute with the client.
        base_logger (Any): The base logger for logging.
        delay (float): The delay in seconds before connecting.
        receive_updates (bool): Whether to receive updates in the session.
        **keyargs (Any): Additional arguments for the callback client.

    Returns:
        None
    """

    try:
        async with Client(
            session,
            api_id, 
            api_hash,
            base_logger,
            delay,
            receive_updates=receive_updates,
            cancelled_event=cancelled_event,
            **keyargs
        ) as client:
            if check_spam:
                spam, _ = await client.check_spambot()
                if spam:
                    base_logger.warning(f'Spam detected {phone}')
                    return
            await callback(client)

    except FatalException:
        raise 

    except Exception as e:
        base_logger.error(f'Error connecting {phone} : {e}')

def get_apis(
    api: Union[Tuple[str, str], Tuple[int, str], Path, str]
) -> List[Tuple[int, str]]:
    """
    Returns the API ID and API hash from the given API.

    Args:
        api (Union[Tuple[str, str], Tuple[int, str], Path, str]): The API ID and API hash.

    Returns:
        List[Tuple(int, str)]: The API ID and API hash.
    """
    if isinstance(api, Path) or isinstance(api, str):
        apis = read_csv(api, drop=True, skip_header=True)
        return [(int(peer[0]), peer[1]) for peer in apis if peer[0].isdigit()]

    if is_list_like(api):
        if is_list_like(api[0]):
            return api
        return [tuple(api)]

    raise ValueError('Invalid API format.')

def get_api(path: Union[Path, str]) -> Tuple[int, str]:
    """
    Returns the API ID and API hash from the given path.

    Args:
        path (Union[Path, str]): The path to the API file.

    Returns:
        Tuple[int, str]: The API ID and API hash.
    """
    api = random.choice(get_apis(path))
    return (api[0], api[1])

async def connect_client(session: Path, api_path='api.csv', base_logger: Logger = _base_loger,) -> Client|None:
    """
    Connects the Telegram client.

    Args:
        session (Path): The path to the session file.

    Returns:
        Client: The Telegram client or None.
    """
    api_id, api_hash = get_api(api_path)
    try:
        client = Client(session, api_id, api_hash, base_logger)
        try:
            await client.start()
            return client
        except Exception as e:
            base_logger.error(f'Error connecting {str(session.stem)} : {e}')
            await client.disconnect()
            return None
        
    except Exception as e:
        base_logger.error(f'Error connecting {str(session.stem)} : {e}')

async def run_task(task, sem, delay_task, *args, **keyargs):
    async with sem:
        await sleep(delay_task)
        return await task(*args, **keyargs)

async def run_app(
    sessions_path,
    api: Union[Tuple[str, str], Tuple[int, str], Path, str],
    callback: Callable[[Client], Any],
    max_tasks: int = 12,
    delay_task: float = 1,
    limit_sessions: int = None,
    base_logger: Logger = _base_loger,
    delay: float = DELAY,
    receive_updates: bool = False,
    check_spam: bool = False,
    black_list_phones: List[str] = [],
    **keyargs
):
    """
    Runs the Telegram client for each session in the given path.

    Args:
        sessions_path (str): The path to the sessions.
        api (Union[Tuple[str, str], Tuple[int, str], Path, str]): The API ID and API hash.
        callback (Callable[[TelegramClient], Any]): The function to execute with the client.
        max_tasks (int): The maximum number of tasks to run concurrently.
        base_logger (Logger): The base logger for logging.
        delay (float): The delay in seconds before connecting.
        receive_updates (bool): Whether to receive updates in the session.

    Returns:
        None
    """
    apis = get_apis(api)
    sessions = [s for s in get_sessions_phones(sessions_path) if s not in black_list_phones]
    random.shuffle(sessions)
    if limit_sessions:
        sessions = sessions[:limit_sessions]

    runner = Runner(name='app', logger=base_logger, max_tasks=max_tasks, delay=delay_task)

    for phone, session in sessions:
        api_choice = random.choice(apis)

        runner.push(
            run_client,
            session=session, 
            phone=phone,
            api_id=api_choice[0], 
            api_hash=api_choice[1], 
            callback=callback, 
            base_logger=base_logger,
            delay=delay, 
            cancelled_event=runner,
            receive_updates=receive_updates, 
            check_spam=check_spam,
            **keyargs
        )

    await runner












