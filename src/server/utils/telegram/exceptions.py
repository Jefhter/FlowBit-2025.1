

from..miscellaneous.async_utils import FatalException
class ClientError(Exception):
    def __init__(self, msg=None, phone=None, tip=None):
        self.msg = msg if msg is not None else self.default_msg
        self.tip = tip if tip is not None else self.default_tip
        self.phone = phone      
            
        super().__init__(self.msg)
        
    def __str__(self):
        return self.msg + '\nTip: ' + self.tip


class PhoneNumberBannedError(ClientError):
    default_msg = "This account has been banned"
    default_tip = "\n"

class PhoneDeslogError(ClientError):
    default_msg = "Session logged out"
    default_tip = "If your session is still logged into your app, you can recreate it"

class ImageDiskMalformedError(ClientError):
    default_msg = "The session file is corrupted"
    default_tip = "Always remember to click Stop before exiting the program, and wait for the process to finish"

class DatabaseLockedError(ClientError):
    default_msg = "Database is locked"
    default_tip = ("Check if there is more than one instance of Ninja open.\n"
                   "If so, close it (You can do this through the task manager).\n"
                   "Keep only one instance of Ninja open at a time, and always finalize the program using Stop.\n"
                   "If the issue persists, restart your computer.")

class SessionHackedError(ClientError):
    default_msg = "Session used on more than one IP at the same time"
    default_tip = ("Remember not to use the same session in more than one program at the same time.\n"
                   "Do not share your session with anyone.\n"
                   "Do not use the main session for additions.\n"
                   "Any of these scenarios can cause you to lose the session.\n"
                   "If you still have it logged in on your phone, you can recreate your session.")

class TimeoutError(ClientError):
    default_msg = "Timeout reached, check your network, proxy, or computer time\n"
    default_tip = ("Due to Telegram's encryption, the computer's time cannot differ by more than 30 seconds "
                   "from the internet's time. Make sure your computer's time matches the network's time.")