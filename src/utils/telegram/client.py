# Copyright (C) 2024 Luigi Augusto Rovani

import random
import asyncio
import os
import re
import string
from pathlib import Path
from logging import getLogger, Logger
from functools import partialmethod, partial
from datetime import datetime

from telethon import TelegramClient, utils, errors, events, types as telethon_types
from telethon.tl.functions import channels, contacts, messages, account
from telethon.tl.functions.phone import GetGroupParticipantsRequest, GetGroupCallRequest
from telethon.tl.functions.users import GetFullUserRequest

from telethon.errors import FloodWaitError, PeerFloodError, AuthKeyDuplicatedError, PhoneNumberBannedError as PhoneNumberBanned

from ..miscellaneous import sleep, convert_iter, Runner, set_loop
from ..miscellaneous.encoding import normalize_to_ascii as unidecode
from ..loggers.colourprinter import colourprinter as colour
from ..loggers import getChilder
from .exceptions import *
from .types import *
from.telethon_utils import parse_phone, clean_phone, clean_session

set_loop()
_base_loger = getLogger('Telegram')
DELAY = os.getenv('CLIENT_DELAY', 0.3)
DEFAULT_TIMEOUT_CONNECT = os.getenv('DEFAULT_TIMEOUT_CONNECT', 10)
API_CODE_PATTERN = r"(?:login code|de login):\s*([\w\-]+)"
LOGIN_CODE_PATTERN = r"\b\d{5}\b"
DATE_SPAMBOT_PATTERN = re.compile(r"(\d{1,2} \w+ \d{4}, \d{2}:\d{2} UTC)")
USER_ID_PATTERN = r"user_id\s*=\s*(\d+)"

class Client(TelegramClient):

    def __init__(
        self,
        session: str | Path,
        api_id: str | int,
        api_hash: str,
        base_logger: Logger = _base_loger,
        delay: float = DELAY,
        receive_updates: bool = False,
        limit_spam_flood: int = 5,
        parse_session : bool = True,
        cancelled_event: Runner = None,
        **kwargs: Any
    ):
        self._session_path: Path = clean_session(session) if parse_session else Path(session)
        self.phone = self._session_path.stem
        self.name = self.phone
        self._me = None
        self.delay = delay
        self.get_update_task = None
        self.flood_count = 0
        self.limit_spam_flood = limit_spam_flood
        self.cancelled_event = cancelled_event
        self.logger = getChilder(self.phone, base_logger)
        self.complete_cache_entity = {'complete': {}, 'base': {}}

        try:
            super().__init__(str(self._session_path), api_id, api_hash, receive_updates=receive_updates, **kwargs)
        except Exception as e:
            if 'database is locked' in str(e).lower():
                e = DatabaseLockedError()
            elif 'disk' in str(e).lower() or 'image' in str(e).lower():
                e = ImageDiskMalformedError()

            msg = e.msg if isinstance(e, ClientError) else  str(e)
            self.logger.error(f'Error in instance of Client {msg}')
            raise e


    @property
    def me(self) -> User | None:
        return self._me

    async def get_me(self, input_peer: bool = False) -> User | None:
        if me := await super().get_me(input_peer=input_peer):
            self._me = me
            self.name = self.get_display(me, 'PINK')
            self.phone = me.phone or self.phone
        return me

    async def _connect_coro(self, request_code, timeout, **kwargs):

        if not self.is_connected():
            await asyncio.wait_for(super().connect(), timeout)

        if kwargs.get('bot_token'):
            await super().start(**kwargs)

        elif request_code:
            await super().start(phone=self.phone, **kwargs)


    async def start(self, request_code=False, timeout=DEFAULT_TIMEOUT_CONNECT, **kwargs):
        self.logger.debug(f'starting connect...')

        try:
            await self._connect_coro(request_code, timeout, **kwargs)

            if me := await super().get_me():
                self.logger.info(f'{self.name} connected successfully.')
                await self.get_dialogs()
                self.create_group_table()
                self.get_update_task = self.loop.create_task(self.update_task())
            else:
                await self.send_code_request(self.phone)
                raise PhoneDeslogError(phone=self.phone)    

            return self

        except Exception as e:

            if isinstance(e, PhoneNumberBanned):
                e = PhoneNumberBannedError()
            elif isinstance(e, AuthKeyDuplicatedError):
                e = SessionHackedError()
            elif isinstance(e, asyncio.TimeoutError):
                e = TimeoutError

            msg = e.msg if isinstance(e, ClientError) else  str(e)
            self.logger.error(f'Error in start client: {msg}')
            raise e

    async def disconnect_close(self, ensure_close):
        self.logger.debug(f'Starting disconnect')
        if self.get_update_task:
            self.get_update_task.cancel()
            await self.get_update_task
            self.get_update_task = None

        try:
            await super().disconnect()
            self.logger.info(f'{self.name} disconnected successfully.')

        except Exception as e:
            self.logger.warning(f'Error in disconnect: {e}')

        if ensure_close:
            try:
                self.session.close()
            except Exception as e:
                pass

        if self._session_path.stem != self.phone:
            self._session_path = self._session_path.with_suffix('.session')
            try:
                self._session_path.rename(self._session_path.with_stem(self.phone))
            except Exception as e:
                self.logger.warning(f'Error in rename session file: {e}')


    async def disconnect(self, ensure_close=False):
        return await self.disconnect_close(ensure_close)
    

    async def update_task(self, delay=12*60*60):
        while self.is_connected():
            try:
                await self.sleep(delay)
                me = await self.get_me()
                await self.set_receive_updates(not self._no_updates)
            except FatalException:
                return 
            
    async def run_callback(self, callback: Callable[[TelegramClient], Any], timeout=None, **kwargs: Any):
        c_name = colour(callback.__name__, 'Y')
        self.logger.debug(f'Starting {c_name}...')
        
        try:
            return await asyncio.wait_for(callback(self, **kwargs), timeout=timeout)

        except (asyncio.CancelledError, KeyboardInterrupt) as e:
            self.logger.warning(f'Shutting down app {c_name} Error: {e.__class__.__name__}')
            raise e
        except Exception as e:
            self.logger.error(f'Error in run {c_name}: {e}')

    def kill_app(self, result: str = None, e: Exception = None):
        self.cancelled_event.finish(result, e)

    async def handle_exception(self, e: Exception) -> bool:

        if isinstance(e, FloodWaitError):
            self.flood_count+=1

            if self.flood_count >= self.limit_spam_flood:
                self.logger.warning(f'Client has reached the flood limit.')
                return True

            self.logger.warning(f'Flood error...sleeping {e.seconds}')
            await self.sleep(e.seconds)

        elif isinstance(e, PeerFloodError):
            self.flood_count+=1

            if self.flood_count >= self.limit_spam_flood:
                self.logger.warning(f'Client has reached the Spam limit.')
                return True

            await self.sleep()

        return False

    async def sleep(self, delay=None):
        if not delay:
            delay = self.delay
        return await sleep(delay)

    async def fetch_admins(self, group: Channel|Chat, ids: bool = True) -> List[User|int]:
        users = []

        try:
            async for user in self.iter_participants(group, filter=ChannelParticipantsAdmins):
                users.append(user)

            if not users:
                users = [user async for user in self.iter_participants(group)]
                if len (users) > 40:
                    users = []

            self.logger.debug(f'Fetched {len(users)} admins from {self.get_display(group)}')

        except Exception as e:
            self.logger.error(f'Error in fetch_admins: {e}')

        return [user.id for user in users] if ids else users

    async def add_user(
        self, 
        user: User|str, 
        channel: Channel|Chat|str, 
        delay: float|int|None =None, 
        join_channel: bool = True,
        fwd_limit: int = 100,
        stack_info: bool = False,
    ) -> None:
        return await self.add_user_to_channel(user, channel, delay, join_channel, fwd_limit, stack_info)

    async def add_user_to_channel(
        self, 
        user: User|str, 
        channel: Channel|Chat|str, 
        delay: float|int|None =None, 
        join_channel: bool = True,
        fwd_limit: int = 100,
        stack_info: bool = False,
    ) -> None:

        if isinstance(channel, str) and join_channel:
            channel = await self.join_channel(channel)

        name_user =  self.get_display(user, 'CYAN')
        name_channel = self.get_display(channel, 'MAGENTA')

        try:
            user = await self.get_complete_entity(user, raise_errors=True, request=True)
            name_user =  self.get_display(user, 'CYAN')
            if isinstance(channel, Chat):
                await self(messages.AddChatUserRequest(self.get_id(channel, add_mask=False), user, fwd_limit))
            else:
                await self(channels.InviteToChannelRequest(channel, [user]))

            self.logger.info(f'Added {name_user} to {name_channel}!')

        except Exception as e:
            self.logger.error(f'Error in add {name_user} to {name_channel}: {e.__class__.__name__}', stack_info=stack_info)
            raise e

        finally:
            await self.sleep(delay)

    async def add_contact(
            self, 
            user: User = None, 
            phone: str = None, 
            first_name: str = '',  
            last_name: str = '', 
            raise_exceptions: bool = False
        ) -> bool:
        try:
            if isinstance(user, User):
                result = await self(contacts.AddContactRequest(
                    user.id,
                    user.first_name or  '',
                    user.last_name  or '',
                    user.phone or '',
                ))
            else:
                result = await self(contacts.ImportContactsRequest([InputPhoneContact(
                    random.randrange(-2**63, 2**63),
                    utils.parse_phone(phone),
                    first_name or '',
                    last_name or ''
                )]))
            self.logger.debug(f'Success in add_contact')
            return getattr(result, 'users', [None])[0]

        except FatalException as e:
            raise e
        except Exception as e:
            self.logger.debug(f'Error in add_contact: {e}')
            if raise_exceptions:
                raise e

        finally:
            await self.sleep()

    async def search_groups(self, key: str, limit: int = 100):
        try:
            results = await self(contacts.SearchRequest(
                q=key,
                limit=limit
            ))
            return results
        except FatalException as e:
            raise e
        except Exception as e:
            await self.logger.debug(f'Error in search_groups: {e}')
            return []
        finally:
            await sleep()

    async def resolve_username(self, username: str) -> User|None:
        result = await self(contacts.ResolveUsernameRequest(username))
        return result.users[0]
        
    async def view_message(
        self, 
        chat_id: int|str|GroupType, 
        msg_id: List[int]|int, 
        increment: bool = True, 
        raise_exceptions: bool = False
    ):
        return await self.view_messages(msg_id, chat_id, increment, raise_exceptions)
        
    async def view_messages(
        self, 
        messages: List[int|Message]|int|Message,
        chat_id: int|str|GroupType = None, 
        increment: bool = True, 
        raise_exceptions: bool = False
    ):
        messages: List[Message] = convert_iter(messages)
        if isinstance(messages[0], Message):
            if not chat_id:
                chat_id = messages[0].chat_id
            messages = [msg.id for msg in messages]

        try:
            await self(messages.GetMessagesViewsRequest(
                peer=chat_id,
                id=messages,
                increment=increment
            ))
        except FatalException as e:
            raise e
        except Exception as e:
            if raise_exceptions:
                raise e
            self.logger.debug(f'Error in view_message: {e}')

    async def react_message(
        self, 
        chat_id: int|str|GroupType, 
        msg_id: int, 
        emoji: str, 
        view: bool = True, 
        big: bool = True, 
        add_to_recent: bool = False, 
        delay: float|int = None,
        prob: float = 1.0
    ):
        if view:
            await self.view_message(chat_id, msg_id)
            await self.sleep(delay)

        try:         
            if random.random() < prob: 
                await self(messages.SendReactionRequest(
                    peer=chat_id,
                    msg_id=msg_id,
                    big=big,
                    add_to_recent=add_to_recent,
                    reaction=[telethon_types.ReactionEmoji(
                        emoticon=emoji
                    )]
                ))
                await sleep(delay)

        except FatalException as e:
            raise e
        except Exception as e:
            self.logger.error(f'Error in react_message: {e}')


    async def get_full_entity(self, entity: EntityLike) -> FullEntity:

        if isinstance(entity, (int, str)):
            entity = await self.get_input_entity(entity)
        if isinstance(entity, FullEntity):
            return entity
        if isinstance(entity, ChannelType):
            return (await self(channels.GetFullChannelRequest(entity))).full_chat
        elif isinstance(entity, ChannelType):
            return (await self(messages.GetFullChatRequest(entity))).full_chat
        elif isinstance(entity, UserType):
            return (await self(GetFullUserRequest(entity))).full_user
        else:
            raise TypeError('Invalid group type')

    async def get_call(self, group: GroupType, limit: int = 100, complete_entity: bool = False) -> InputGroupCall|GroupCall|None:
        full_chat = await self.get_full_entity(group)

        if hasattr(full_chat, 'call') and full_chat.call:
            result = await self(GetGroupCallRequest(full_chat.call, limit))
            if complete_entity:
                return result

            call = full_chat.call
            call.active = not bool(result.call.schedule_date)
            return call

    async def get_emojis(self, group: GroupType) -> List[str]:
        return [react.emoticon for react in (await self.get_complete_entity(group, True)).available_reactions]

    async def get_emoji(self, group: GroupType, fallback_emojis: List[str] = []):

        try:
            emojis = [react for react in (await self.get_emojis(group)) if (not fallback_emojis or react in fallback_emojis)]
            if emojis:
                return random.choice(emojis).strip()
        except Exception as e:
            if fallback_emojis:
                return random.choice(fallback_emojis).strip()
            raise e

    async def get_complete_entity(self, input_entity: EntityLike, complete=False, raise_errors=False, request=False) -> Entity | FullEntity | None:
        last_try = False
        entity = None
        entity_id = self.get_id(self.get_cached_entity(input_entity))
        key = 'complete' if complete else 'base'

        if not entity_id:
            if request:
                try:
                    if username := getattr(input_entity, 'username', None):
                        entity = await self.get_input_entity(username)
                    elif phone := parse_phone(getattr(input_entity, 'phone', '')):
                        entity = await self.add_contact(phone)
                    else:
                        entity = await self.get_input_entity(input_entity)
                    entity_id = self.get_id(entity)

                except Exception as e:
                    entity_id = None

            if not entity_id:
                if raise_errors:
                    raise ValueError(f'Entity not provid')
                return None

        if not entity:
            try:
                entity = self.complete_cache_entity[key][entity_id]
                if entity is not None:
                    if entity:
                        return entity
                    if raise_errors:
                        raise ValueError(f'Entity not found: {entity_id}')
                    return None
                last_try = True
            except KeyError:
                pass

        try:
            if complete:
                entity = await self.get_full_entity(entity_id)
            else:
                entity = await self.get_entity(entity_id)

            self.complete_cache_entity[key][entity_id] = entity
            return entity

        except ValueError as e:
            self.complete_cache_entity[key][entity_id] = '' if last_try else None
            if raise_errors:
                raise ValueError(f'Entity not found: {entity_id}')

    async def fetch_participants_from_call(
        self,
        call: InputGroupCall,
        group: GroupType, 
        max_requests: int = 20, 
        limit: int  = 100
    )-> List[User]:

        users = []
        offset = ''

        for _ in range (max_requests):
            result = await self(GetGroupParticipantsRequest(
                call=call,
                ids=[],
                sources=[],
                offset=offset,
                limit=limit
            ))
            users.extend(result.users)

            if len(users) >= result.count-2:
                break 

            offset = result.next_offset
            await self.sleep()

        self.logger.info(f'Fetched {len(users)} participants from {self.get_display(group)}')
        return users


    async def update_username(self, username: str = None, force: bool = False) -> str:
        me = await self.get_me()
        if me.username and not force:
            self.logger.debug(f'{self.name} ja possui username: {me.username}')
            return me.username
        
        if not username:
            base = unidecode(self.name.lower().replace(" ", "")[:24])
            random_str  = ''.join(random.choices(string.digits, k=5))
            username = base + random_str
            
        try:
            await self(account.UpdateUsernameRequest(username))
        except Exception as e:
            self.logger.debug(f'Error in change username to {self.name} | {username} : {e}')
            return ''
        else:
            self.logger.debug(f' Sucess change username for {self.name} | {username}')
            return username

    async def response_callback(self, event:UpdateNewMessage, done_event=None, result=None):
        result.append(event.message)
        done_event.set()
        raise events.StopPropagation 

    async def get_response_msg(
        self, 
        chat_id: IterChatInputType,
        func: Callable[[Message], bool]|None = None, 
        regex: str|None = None,
        timeout: int = 300
    ) -> Message|None:

        if self._no_updates:
            await self.set_receive_updates(True)

        done_event = asyncio.Event()
        result=[]
        callback = partial(self.response_callback, done_event=done_event, result=result)
        event = events.NewMessage(convert_iter(chat_id), incoming=True, func=func, pattern=regex)
        self.add_event_handler(callback, event)

        try:
            await asyncio.wait_for(done_event.wait(), timeout)
            return result[0]
        except asyncio.TimeoutError:
            return None
        finally:
            self.remove_event_handler(callback, event)

    async def ask_msg(
        self, 
        chat_id: EntityLike, 
        question: str, 
        fall_question: str = None,
        max_attempts: int = 3,
        timeout: int = 300, 
        func: Callable[[Message], bool]|None = None, 
        regex: str|None = None,       
        **kwargs
    ) -> Message|None:
        message: Message = await self.send_message(chat_id, question, **kwargs)

        async def _ask_msg():
            for attempt in range(max_attempts):
                if response := await self.get_response_msg(chat_id, timeout=timeout):
                    if (not func) or (func(response)):
                        if (not regex):
                            return response
                        if matchs := re.search(regex, response.message):
                            response.matchs = matchs
                            return response

                    await self.response.reply(fall_question or question)

        return await asyncio.wait_for(_ask_msg(), timeout)
        
    async def get_code(self, api = False, timeout = 300, bot_id = 777000) -> str:
        pattern = API_CODE_PATTERN if api else LOGIN_CODE_PATTERN
        if message := await self.get_response_msg(bot_id, regex=pattern, timeout=timeout):
            return re.search(message.text).group(0)

    async def search_users_from_tl(self, obj):
        users = []
        for user_id in self.search_users_ids(obj):
            if user := await self.get_complete_entity(user_id):
                users.append(user)
                continue

        return self.filter_users(users)

    async def fetch_users_from_reply(self, channel: ChannelInputType, message: Message) -> List[User]:
        offset = 0
        users = []
        while offset < message.replies.replies:
            reply = await self(messages.GetRepliesRequest(
                peer=channel,
                msg_id=message.id,
                offset_id=0,  
                offset_date=None,
                add_offset=offset,
                limit=100,  
                max_id=0,
                min_id=0,
                hash=0                            
            ))
            users += reply.users
            offset += len(reply.messages)
            await self.sleep()
            if not reply.messages:
                break

        return self.filter_users(users)

    async def fetch_users_from_message(self, message: int|Message, group: Channel|Chat|None, delay: int|float = 0) -> List[User]:
        def check_replies():
            return message.replies and message.replies.replies > 0

        if isinstance(group, Channel) and group.broadcast:
            if check_replies():
                await self.sleep(delay)
                return await self.fetch_users_from_reply(group, message)
            return []

        if isinstance(message, Message):
            users = []
            if message.reactions:
                try:
                    result = await self(messages.GetMessageReactionsListRequest(
                        peer=group, id=message.id, limit=100
                    ))
                    users.extend(result.users)
                    self.logger.debug(f'found {len(users)}')
                except Exception as e:
                    self.logger.debug(f'Error in get reactions: {e}')
                    users.extend((await self.search_users_from_tl(message.reactions)))

            users.append(message.sender)
            return self.filter_users(users) 
        
        return []

    async def fetch_users_from_messages(self, group: Channel|Chat, limit: int = 20, delay: int|float = None, **kwargs) -> List[User]:
        if not isinstance(group, GroupEntity):
            group = await self.get_complete_entity(group, raise_errors=True, request=True)

        async for message in self.iter_messages(group, limit=limit, **kwargs):
            users += (await self.fetch_users_from_message(message, group, delay))

        return self.filter_users(users)

    async def fetch_all_participans(self, channel: Channel, delay: int|float = None, filter=None) -> List[User]:
        pattern = re.compile(r"\b[a-zA-Z]")
        users = []
    
        for key in list(string.ascii_lowercase):
            offset, limit = 0, 199
            while True:
                participants = await  self(
                    channels.GetParticipantsRequest(
                        channel, telethon_types.ChannelParticipantsSearch(key), offset, limit, hash=0
                    )
                )
                if not participants.users:
                    break

                for participant in participants.users:
                    try:
                        if pattern.findall(participant.first_name)[0].lower() == key:
                            users.append(participant)
                    except Exception:
                        pass
                        
                offset += len(participants.users)
                await self.sleep(delay)

        return self.filter_users(users, filter)

    async def get_chat_id(self, chat_id, add_mask=False) -> int|None:
        if isinstance(chat_id, int):
            pass
        elif isinstance(chat_id, Message):
            chat_id = chat_id.from_id
        elif hasattr(chat_id, 'get_sender'):
            chat_id = await (await chat_id.get_sender()).id
        elif hasattr(chat_id, 'get_input_chat'):
            chat_id = await (await chat_id.get_input_chat())
        else:
            try:
                chat_id = await self.get_input_entity(chat_id)
            except:
                pass

        if chat_id := self.get_id(chat_id, add_mask):
            return chat_id
        raise ValueError(f"Unable to resolve sender ID from TypeUpdates object: {chat_id}")
            

    def get_display(self, entity, color: str = 'LM') -> str:

        if isinstance(entity, dict) and entity.get('name'):
            display_name = entity['name']
        else:
            display_name = utils.get_display_name(entity)

        if not display_name:

            if cached_entity := self.get_cached_entity(entity, False):
                display_name = cached_entity['name']

            elif group := self.get_group_info(entity):
                display_name = group['name']

            elif isinstance(entity, (str, int)):
                display_name = str(entity)
            else:
                display_name = ''

        return colour(display_name if display_name else '', color)

    async def leave_channels(self, limit: int = 5):
        count = 1
        self.logger.debug(f'Leaving channels...')

        async for dialog in self.iter_dialogs():
            try:
                if not dialog.is_channel:
                    continue
                
                if self.get_group_info(dialog.entity):
                    continue

                count+=1
                result = await self(channels.LeaveChannelRequest(channel=dialog.entity))
                self.logger.debug(f'leave sucess channel {result.chats[0].title}')

            except FloodWaitError:
                break
            except FatalException as e:
                raise e
            except Exception as e:
                self.logger.debug(f'Error in leave channel: {e}')

            if count >= limit:
                break

    async def check_group(self, entity: EntityLike, check_add=False) -> None|Chat|Channel:
        entity = await self.get_complete_entity(entity, raise_errors=True, request=True)

        if any ([
            isinstance(entity, BannedGroupType),
            isinstance(entity, Channel) and (entity.restricted and entity.banned_rights.view_messages),
            isinstance(entity, GroupEntity) and entity.left
        ]):
            raise ValueError(f'Kicked in {self.get_display(entity)}!')

        if check_add and entity.default_banned_rights.invite_users:
            self.logger.error(f'Not permission to add in {self.get_display(entity)}!')
            return None

        return entity

    async def _join_channel(self, username_link: str, second_try=False) -> None: 
        try:
            await self(channels.JoinChannelRequest(username_link))

        except errors.ChannelsTooMuchError:
            self.logger.warning(f'ChannelsTooMuchError')
            if not second_try:
                await self.leave_channels()
                return await self._join_channel(username_link, True)

        except Exception as e:
            self.logger.error(f'Error in join_channel {e}')

    async def join_chat(self, acess_hash: str, second_try=False) -> None:

        try:
            await self(messages.ImportChatInviteRequest(acess_hash))
            
        except errors.ChannelsTooMuchError:
            self.logger.warning(f'ChannelsTooMuchError')
            if not second_try:
                await self.leave_channels()
                return await self.join_chat(acess_hash, True)

        except errors.UserAlreadyParticipantError:
            pass
        except errors.InviteRequestSentError as e:
            self.logger.warning(f'Client awaiting approval to chat')
            if not second_try:
                await self.sleep(3)
                return await self.join_chat(acess_hash, True)
            raise e

        except Exception as e:
            self.logger.error(f'Error in join_chat {e}')    


    async def join_channel(self, link: str) -> Channel|Chat|None:
        """Join channel or chat. Return entity or None"""
        
        try:
            try:
                peer = self.get_cached_entity(link, resolve=True)
            except Exception:
                peer = None

            info_group, retry = self.check_joined(peer, link)

            if info_group:
                self.logger.debug(f'client already part of group {info_group["name"]}!')
                return await self.get_complete_entity(info_group['id'])

            if not info_group and retry:
                self.logger.debug(f'Error in join_channel {link}')
                return None
             
            acess_hash, is_invite = utils.parse_username(link)
            if is_invite:
                await self.join_chat(acess_hash)
            else:
                await self._join_channel(link)
            
            entity = await self.check_group(link)
            self.logger.info(f'Success join in {self.get_display(entity, 'LC')}')
            self.add_joined_group(entity, link)
            return entity

        except FatalException as e:
            raise e

        except Exception as e:
            self.logger.error(f'Error in join_channel {e}')
            self.add_error_join_group(peer, link)

    async def join_group(self, link: str) -> Channel|Chat|None:
        return await self.join_channel(link)

    def get_query(self, query: str, data: Tuple = (), to_dict: bool = True) -> List[Tuple[Any]|Dict[str,Any]]:
        c = self.session._cursor()
        c.execute(query, data)
        result = c.fetchall()

        if to_dict and result:
            column_names = [col[0] for col in c.description]
            result = [
                dict(zip(column_names, row))
                for row in result
            ]

        c.close()
        return result

    def execute_query(self, query: str, data: Tuple|None = None) -> None:
        c = self.session._cursor()
        try:
            if data:
                c.execute(query, data)
            else:
                c.execute(query)
            self.session.save()
        except Exception as e:
            self.logger.debug(f'Error in execute_query: {e}')
            return
        finally:
            c.close()
        
    def get_cached_entity(self, entity, resolve = True) -> Dict[str, Any]| None:
        try:
            resolved_entity = self.session.get_input_entity(entity)
        except ValueError:
            resolved_entity = None 
        
        if resolve:
            return resolved_entity

        query = 'SELECT * FROM entities WHERE id = ?'
        if entity_id := self.get_id(resolved_entity or entity, add_mask=True):
            result = self.get_query(query, (entity_id,), to_dict=True)
            return result[0] if result else None


    async def _check_spambot(self) -> Tuple[bool, datetime|None]:
        spambot = 'SpamBot'
        spamtext = [
            "no limits are currently applied to your account",
            "nenhum limite foi aplicado",
            "livre como um",
            "free as a bird"
        ]

        try:
            msg = await self.ask_msg(spambot, '/start', timeout=3)
            msg = msg.text

            if any (text in msg for text in spamtext):
                self.logger.debug(f'Client is good')
                return False, None

            if date_match := DATE_SPAMBOT_PATTERN.search(msg):
                date_limitation = datetime.strptime(date_match.group(1), '%d %b %Y, %H:%M %Z')
                self.logger.debug(f'Client is a spam until {date_limitation}')
                return True, date_limitation
            return True, None

        except FatalException as e:
            raise e

        except Exception as e:
            if 'blocked this user' in str(e).lower():
                self.logger.debug(f'Client blocked spambot\n Try again ')
                return False, None
            self.logger.error(f'Error in check_spambot: {e}')
            return True, None

    async def check_spambot(self, user_cache=True) -> Tuple[bool, datetime|None]:
        timestamp = int(datetime.now().timestamp())

        if user_cache:
            query = """
                SELECT spam, date_unblock  FROM spam_bot 
                WHERE check_at > ?
                ORDER BY check_at DESC
                LIMIT 1
            """
            data = (timestamp - 24*60*60,)
            if result := self.get_query(query, data):
                spam = result[0]['spam']
                date_unblock = result[0]['date_unblock']
                if date_unblock:
                    return spam, datetime.fromtimestamp(date_unblock)
                return spam, None

        spam, date_unblock = await self._check_spambot()

        if date_unblock:
            query = 'INSERT INTO spam_bot (check_at, spam, date_unblock) VALUES (?, ?, ?)'
            data = (timestamp, 1 if spam else 0, int(date_unblock.timestamp()))
        else:
            query = 'INSERT INTO spam_bot (check_at, spam) VALUES (?, ?)'
            data = (timestamp, 1 if spam else 0)

        self.execute_query(query, data)
        return spam, date_unblock


    def create_group_table(self):
        self.execute_query("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY, 
                link TEXT UNIQUE,
                name TEXT,
                broadcast INTEGER DEFAULT 0,
                raised_errors INTEGER DEFAULT 0,
                joined INTEGER DEFAULT 0
            )
        """)

        self.execute_query("""
            CREATE TABLE IF NOT EXISTS spam_bot (
                id INTEGER PRIMARY KEY, 
                check_at INTEGER,
                spam INTEGER DEFAULT 0,
                date_unblock INTEGER
            )
        """)

    def add_joined_group(self, group: Chat|Channel, link: str):
        group_id = self.get_id(group)
        name = utils.get_display_name(group)
        broadcast = 1 if isinstance(group, Channel) and group.broadcast else 0
        data = (group_id, link, name, broadcast, 0, 1)
        query = """
            INSERT INTO groups (id, link, name, broadcast, raised_errors, joined)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                link = excluded.link,
                name = excluded.name,
                broadcast = excluded.broadcast,
                raised_errors = excluded.raised_errors,
                joined = excluded.joined
        """
        self.execute_query(query, data)

    def check_joined(self, group: GroupType, link: str) -> Tuple[bool|Dict, bool]:
        group_id = self.get_id(group)
        if group_id:
            query = 'SELECT * FROM groups WHERE id = ?'
            data = (group_id, )
        elif link:
            query = 'SELECT * FROM groups WHERE link = ?'
            data = (link, )
        else:
            return False, False

        if result := self.get_query(query, data, to_dict=True):
            group = result[0]
            info = group if group['joined'] else False
            retry = group['raised_errors'] > 4
            return info, retry

        return False, False

    def add_error_join_group(self, group: GroupType, link: str):
        group_id = self.get_id(group)

        if group_id:
            query = """
                INSERT INTO groups (id, link, joined)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    link = excluded.link,
                    joined = excluded.joined
            """
            data = (group_id, link, 1)
            self.execute_query(query, data)
            self.execute_query('UPDATE groups SET raised_errors = groups.raised_errors + 1 WHERE id = ?', (group_id, ))

        elif link:
            query = """
                INSERT INTO groups (link, joined)
                VALUES (?, ?)
                ON CONFLICT (link) DO UPDATE SET
                    joined = excluded.joined
            """
            data = (link, 1)
            self.execute_query(query, data)
            self.execute_query('UPDATE groups SET raised_errors = groups.raised_errors + 1 WHERE link = ?', (link,))

    def get_group_info(self, group: GroupType) -> Dict[str, Any]|None:
        if group_id := self.get_id(group):
            if result := self.get_query('SELECT * FROM groups WHERE joined = 1 and id = ?', (group_id,)):
                return result[0]

    # staticmethods region
    @staticmethod
    def colour(text: str, color: str) -> str:
        return colour(text, color)

    @staticmethod
    def get_msg_ids(msgs) -> List[int]:
        return [utils.get_message_id(m) for m in convert_iter(msgs) if m]

    @staticmethod
    def get_id(entity, add_mask=True) -> int|None:
        try:
            if isinstance(entity, dict):
                entity = entity.get('id', entity)
            peer_id = utils.get_peer_id(entity, add_mask)
            return peer_id or None
        except Exception:
            return None

    @staticmethod
    def search_users_ids(obj) -> List[int]:
        return [int(user_id) for user_id in re.findall(USER_ID_PATTERN, str(obj))]

    @staticmethod
    def filter_users(users: Iterable[User], filter=None) -> List[User]:
        _filter = filter or (lambda user: True)
        def _filter_user(user: User) -> bool:
            return (user and isinstance(user, User)
                    and not user.bot and not user.is_self
                    and _filter(user))

        return list({
            user.id: user
            for user in convert_iter(users)
            if _filter_user(user)
        }.values())

    @staticmethod
    def filter_user_rows(users_rows: Iterable[List[str]], filter=None) -> List[List[str]]:
        filter = filter or (lambda row: True)
        return list({
            row[0]: row
            for row in users_rows
            if filter(row)
        }.values())

    @staticmethod
    def parse_phone(phone: str|int) -> str:
        return parse_phone(phone)

    @staticmethod
    def clean_phone(phone: str|int|Path) -> str:
        return clean_phone(phone)

    @staticmethod
    def clean_session(session_path: str|Path) -> Path:
        return clean_session(session_path)

    @staticmethod
    def is_entity(obj: Any) -> bool:
        return isinstance(obj, (User, Channel, Chat))
