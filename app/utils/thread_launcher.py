import asyncio
import random
import secrets
from threading import Thread
from typing import Callable


def run_service(**kwargs) -> None:
    """
    Runs a given batch service using new event loop.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_and_run_service(**kwargs))
    return


async def initialize_and_run_service(service_class: Callable, **kwargs) -> None:
    """
    Initializes and runs a given service
    (depending on service_class argument and kwargs)
    """
    await asyncio.sleep(random.randint(1, 5))
    service_instance = service_class(**kwargs)
    await service_instance.run_service()


def run_in_new_thread(**kwargs) -> None:
    """
    Executes a sync function in a new thread.
    """
    thread_name = kwargs.pop('thread_name') if kwargs.get('thread_name') else f'Thread_{secrets.token_urlsafe(3)}'

    thread = Thread(target=run_service, kwargs=kwargs, name=thread_name)
    thread.start()
