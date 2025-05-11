import logging
import asyncio
import random
import os
import warnings
from functools import partial
from typing import List, Optional, Union, Any
from collections.abc import AsyncIterable, Coroutine, Iterable, Callable, Awaitable

from .os_utils import *
from .utils import *
from .decorators import ensure

__all__ = ['sleep', 'run_async', 'Runner', 'get_loop', 'get_runner', 'set_loop']

DELAY = float (os.getenv('DELAY', 0.5))
DELAY_FACTOR = int(os.getenv('DELAY_FACTOR', 10))
FatalException = (SystemExit, asyncio.CancelledError, KeyboardInterrupt)

async def sleep(delay: float|int = DELAY, factor: int = DELAY_FACTOR) -> None:
    """ Sleeps for a random time in average delay seconds if delay is not None and > 0"""
    if delay:
        await asyncio.sleep(random.uniform(
            delay/factor, 
            delay*2
        ))

async def run_async(
    iterable: Iterable | AsyncIterable, 
    func: Callable[..., Coroutine[Any, Any, Any]], 
    parallel: bool = True, 
    return_exceptions: bool = True,
    **kwargs: Any
) -> Awaitable[Any]:

    if check_async_iterable(iterable):
        async for item in iterable:
            await func(item, **kwargs)

    elif parallel:
        return await asyncio.gather(
            *[func(item, **kwargs) for item in convert_iter(iterable)], 
            return_exceptions=return_exceptions
        )

    else:
        for item in convert_iter(iterable):
            await func(item, **kwargs)


def set_loop() -> None:
    if os_is_linux():
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            warnings.warn('Use uvloop for better performance')

def get_runner():
    if os_is_linux():
        try:
            import uvloop
            return uvloop
        except ImportError:
            warnings.warn('Use uvloop for better performance')
    return asyncio

def get_loop() -> asyncio.AbstractEventLoop:
    set_loop()
    return asyncio.get_event_loop()


class Runner:
    def __init__(
        self, 
        coros: List[asyncio.Future]|asyncio.Future = [], 
        name: Optional[str] = __name__, 
        max_tasks: Optional[int] = None, 
        logger: Optional[logging.Logger] = None, 
        raise_exceptions: bool = False, 
        raise_cancel_exception: bool = True,
        delay: Optional[Union[float, int]] = None,
        timeout: Optional[float] = None,
        debug: bool = False,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.name: str = name
        self.raise_cancel_exception: bool = raise_cancel_exception
        self.raise_exceptions: bool = raise_exceptions
        self.logger: Optional[logging.Logger] = logger
        self.timeout: Optional[float] = timeout
        self.delay: Optional[Union[float, int]] = delay
        self._e  = None
        self._sem: Optional[asyncio.Semaphore] = None
        self.max_tasks = max_tasks
        self._tasks: List[asyncio.Future] = []
        self.loop: asyncio.AbstractEventLoop = loop
        self.debug = debug
        self.tasks = coros

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        if not logger:
            self._logger = logging.getLogger(self.name)
            self._logger.setLevel(logging.CRITICAL)
        else:
            self._logger = logger.getChild(self.name)

    @property
    def loop(self):
        return self._loop

    @loop.setter
    @ensure
    def loop(self, loop: asyncio.AbstractEventLoop|None = None):
        if self.loop and self.pending:
            raise RuntimeError('Cannot change loop while tasks are running')

        self._loop = loop or get_loop()

    @property
    def max_tasks(self):
        return self._sem._value if self._sem else None

    @max_tasks.setter
    def max_tasks(self, max_tasks: int):
        if not self._sem:
            self._sem = asyncio.Semaphore(max_tasks) if max_tasks else None
        elif max_tasks:
            self._sem._value = max_tasks

    @property
    def tasks(self) -> List[asyncio.Task]:
        return [task for task in self._tasks if not task.cancelled()]

    @tasks.setter
    def tasks(self, tasks):
        for task in convert_iter(tasks):
            if isinstance(task, (asyncio.Future, asyncio.Task)):
                self._tasks.append(task)
            elif isinstance(task, partial):
                self.push(task.func, *task.args, **task.keywords)
            else:
                self.push(task)

    @property
    def results(self):
        for task in self.tasks:
            if task.done() and not task.exception():
                yield task.result()

    @property
    def all_results(self):
        for task in self.tasks:
            if task.done():
                yield task.result()

    @property
    def pending(self):
        return [task for task in self.tasks if not task.done()]

    async def _run_coro(self, coro, *args, **keyarg):
        name = coro.__name__
        if self.delay:
            await sleep(self.delay)
        
        try:
            result = await asyncio.wait_for(coro(*args, **keyarg), self.timeout)
            self.logger.debug(f'Finished: {name}')
            return result
        except asyncio.TimeoutError:
            self.logger.debug(f'Timeout: {name}', exc_info=self.debug)
        except asyncio.CancelledError:
            self.logger.warning(f'Cancelled: {name}', exc_info=self.debug)
            raise
        except FatalException:
            self.logger.warning(f'ShutDown: {name}')
            raise
        except Exception as e:
            self.logger.error(f'Error: {e}', exc_info=self.debug)
            raise
            
    def push(self, coro, *args, **keyarg):
        async def run_coro():
            if self._sem:
                async with self._sem:
                    return await self._run_coro(coro, *args, **keyarg)
            else:
                return await self._run_coro(coro, *args, **keyarg)

        task = self.loop.create_task(run_coro())
        self._tasks.append(task)
        return task

    def __await__(self):
        return self.run().__await__()

    async def run(self):

        try:
            await asyncio.gather(*self.pending, return_exceptions=not self.raise_exceptions)

        except asyncio.CancelledError:
            self.logger.warning("Cancelled")
            if self.raise_cancel_exception:
                raise

        except Exception as e:
            self.logger.error(f"Error: {e}", exc_info=self.debug)
            if self.raise_exceptions:
                raise

        else:
            self.logger.info("All tasks finish")

        if self._e:
            raise self._e

        return self.results

    def _cancel_all(self, result, e):
        for task in self.pending:
            task.cancel()

        if e:
            self.logger.error(f"Cancelled with error: {e}")
            self._e = e
        else:
            self.logger.info(result)

    def cancel(self, result = None, e = None):
        self.loop.call_soon(self._cancel_all, result, e)

    def finish(self, result = None, e = None):
        self.cancel(result, e)



