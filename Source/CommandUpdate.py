#
# CommandUpdate.py
# Botpy
#
# Created by Ashish Ahuja on 5th October 2017.
# This file is licensed under the MIT License.
#

import subprocess

from BotpySE import Command, Utilities


class CommandUpdate(Command):
    @staticmethod
    def usage():
        return ["update", "pull"]

    def run(self):
        print("UPDATE")
        subprocess.call(['git', 'pull', 'origin', 'master'])
        self.reply("Updating...")
        Utilities.StopReason.reboot = True
