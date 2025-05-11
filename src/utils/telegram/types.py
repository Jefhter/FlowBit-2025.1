from typing import Any, Callable, Iterable, List, Tuple, Dict, Awaitable, Union
from telethon import types as telethon_types
from telethon.types import Message
from telethon.hints import Entity, EntityLike, FullEntity, MessageIDLike
from telethon import hints

from telethon.tl.types import (
    InputPhoneContact, ChannelParticipantsAdmins, 
    InputGroupCall, GroupCall,
    User, Channel, Chat, Message, TypeUpdate,
    InputPeerUser, UpdateNewMessage
)

GroupEntity = telethon_types.Chat | telethon_types.Channel
ChatType = telethon_types.Chat | telethon_types.InputPeerChat | telethon_types.PeerChat
ChannelType = telethon_types.Channel | telethon_types.InputPeerChannel | telethon_types.PeerChannel
UserType = telethon_types.User | telethon_types.InputPeerUser | telethon_types.PeerUser
GroupType = telethon_types.Chat | telethon_types.InputPeerChat | telethon_types.Channel | telethon_types.InputPeerChannel | telethon_types.PeerChat | telethon_types.PeerChannel
BannedGroupType = telethon_types.ChannelForbidden | telethon_types.ChatEmpty | telethon_types.ChatForbidden

ChatInputType = ChatType | UserType | int | str 
ChannelInputType = ChannelType | int | str
UserInputType = UserType | int | str
MessageInputType = Message | str | int

IterChatInputType = Union[ChatInputType, List[ChatInputType]]
IterChannelInputType = Union[ChannelInputType, List[ChannelInputType]]
IterUserInputType = Union[UserInputType, List[UserInputType]]
IterMessageInputType = Union[MessageInputType, List[MessageInputType]]
