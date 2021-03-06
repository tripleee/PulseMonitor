import json
import re

from BotpySE import Command


class Notifications:
    def __init__ (self, rooms, filename='./notifications.json'):
        self.notifications = dict()
        self.filename = filename
        self.users = dict()
        try:
            with open(filename, 'r') as notifications_file:
                notifications, users = json.load(notifications_file)
            self.notifications = notifications
            self.users = users
        except FileNotFoundError:
            pass
        for room in rooms:
            room = str(room)
            if room not in self.notifications:
                self.notifications[room] = dict()

    def save (self, filename=None):
        if filename is None:
            filename = self.filename
        with open(filename, 'w') as notifications_file:
            json.dump([self.notifications, self.users], notifications_file)

    def add (self, room, regex, user_id, user_name):
        room = str(room)
        user_id = str(user_id)
        self.users[user_id] = user_name
        try:
            _ = re.compile(regex)
            self.notifications[room][regex].append(user_id)
        #except re.error: regex compilation failed
        except KeyError:
            self.notifications[room][regex] = [user_id]
        self.save()

    def remove(self, room, regex, user):
        room = str(room)
        user = str(user)
        self.notifications[room][regex].remove(user)
        #except ValueError:  user not in list for regex
        #except KeyError: regex not in notifications
        if self.notifications[room][regex] == []:
            del self.notifications[room][regex]
        if self.notifications[room] == {}:
            del self.notifications[room]

    def list(self):
        for room in self.notifications:
            for regex in self.notifications[room]:
                for user in self.notifications[room][regex]:
                    yield room, regex, user, self.users[str(user)]

    def remove_matching(self, room, user, expr):
        r = re.compile(expr)
        #except re.error:
        remove = []
        for room, regex, user_id, user_name in self.list():
            if r.search(regex):
                remove.append(regex)
        for regex in remove:
            self.remove(room, regex, user_id)
        self.save()
        return remove


    def filter_post(self, room, post):
        room = str(room)
        if room not in self.notifications:
            self.notifications[room] = dict()
        notifications = set()
        for regex in self.notifications[room]:
            if re.search(regex, post):
                notifications.update(self.notifications[room][regex])
        if notifications:
            return ' '.join([post] + [
                '@{0}'.format(self.users[str(user)]) for user in notifications])
        #else
        return post


class CommandNotifications(Command):
    @staticmethod
    def usage():
        return ["notifications"]

    def run(self):
        print("NOTIFICATIONS")
        for room, regex, user_id, user_name in \
                self.command_manager.notifications.list():
            self.reply(
                "Active notification: {0} {1!r}".format(user_name, regex))


class CommandNotify(Command):
    @staticmethod
    def usage():
        return ["notify ..."]

    def run(self):
        room = self.message.room.id
        user_id = self.message.user.id
        user_name = self.message.user.name
        regex = ' '.join(self.arguments)
        print("NOTIFY {0} for {1}".format(user_id, user_name, regex))
        try:
            self.command_manager.notifications.add(
                room, regex, user_id, user_name)
            self.reply(
                'Added notification for {0} for {1}'.format(user_name, regex))
        except re.error as err:
            self.reply('Could not add notification {0}: {1}'.format(regex, err))


class CommandUnnotify(Command):
    @staticmethod
    def usage():
        return ["unnotify ..."]

    def run(self):
        room = self.message.room.id
        user = self.message.user.id
        pat = ' '.join(self.arguments)
        print("UNNOTIFY {0} for {1}".format(pat, self.message.user.name))
        removed = []
        try:
            removed = self.command_manager.notifications.remove_matching(
                room, user, pat)
        except re.error as err:
            self.reply('Could not remove {0}: {1}'.format(pat, err))
            return False
        if not removed:
            self.reply('No matches on {0}'.format(pat))
            return False
        self.reply('Removed notifications {0!r}'.format(removed))
