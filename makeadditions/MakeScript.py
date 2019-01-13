"""
This class represents and stores the tasks and commands from a
Makefile (and a specific target). It can be printed as an .sh-script
"""

import re
from os import linesep, path
from sys import stderr
from .execute import run_make_with_debug_shell
from .parse import (
    check_debugshell_and_makefile,
    translate_to_commands
)


class MakeScript:

    """
    The sh-script representation of the tasks from a Makefile
    """

    def __init__(self):
        """ Just init an empty makefile """

        # List for all commands
        self.cmds = []

        # Dictionary of all generated libraries
        self.libs = dict()

        self.lib_deps = dict()

    def register(self, cmd):
        """ Extract and store informations needed by other commands """
        #print("Register command " + cmd.bashcmd)
        # look for generated libraries
        lib = None
        new_lib = None
        if cmd.bashcmd.startswith("ar "):
            libmatch = re.search(
                r"ar [-]?[cruqs]+ ([^ ]*lib([^ ]+)\.a)", cmd.bashcmd)
            if libmatch:
                lib = "lib" + libmatch.group(2)
                new_lib = path.join(cmd.curdir, libmatch.group(1) + ".bc")
                self.libs[lib] = new_lib
        if cmd.bashcmd.startswith("/usr/local/bin/llvm-link "):
            libmatch = re.search(
                r"llvm-link [-]?[o]+ ([^ ]*lib([^ ]+)\.a)", cmd.bashcmd)
            if libmatch:
                lib = "lib" + libmatch.group(2)
                new_lib = path.join(cmd.curdir, libmatch.group(1) + ".bc")
                self.libs[lib] = new_lib
        if cmd.bashcmd.startswith("/usr/local/bin/llvm-link "):
            libmatch = re.search(
                r"llvm-link [-]?[o]+ ([^ ]*lib([^ ]+)\.a.bc)", cmd.bashcmd)
            if libmatch:
                lib = libmatch.group(1)[:-3]
                new_lib = path.join(cmd.curdir, libmatch.group(1))
                #print("Add lib " + lib + " " + path.join(cmd.curdir, libmatch.group(1)))
                self.libs[lib] = new_lib
        if cmd.bashcmd.startswith("/usr/bin/ar ") or cmd.bashcmd.startswith("/usr/local/bin/llvm-ar "):
            libmatch = re.search(
                r"ar [-]?[qc]+ ([^ ]*lib([^ ]+)\.a)", cmd.bashcmd)
            if libmatch:
                lib = "lib" + libmatch.group(2)
                new_lib = path.join(cmd.curdir, libmatch.group(1) + ".bc")
                self.libs[lib] = new_lib
        if not new_lib:
            return

        new_lib = path.basename(new_lib)
        print("Created lib " + new_lib)
        for dep in cmd.bashcmd.split():
            if not dep.endswith(".bc"):
                continue
            if new_lib == dep:
                continue
            #print("Dependent on lib " + dep)
            self.lib_deps[new_lib] = self.lib_deps.get(new_lib, [])
            self.lib_deps[new_lib].append(dep)
        #
        # print("\n")
        # print(self.lib_deps)
        # print("\n")

    # pylint: disable=no-self-use
    def transform(self, cmd):
        """ Apply transformation to the vanilla command before it is stored """
        return cmd

    @classmethod
    def from_makefile(cls, makefile, targets=None):
        """ Alternative constructor from makefile on the filesystem """
        targets = targets or ["all"]

        # Start with an empty Makescript
        new = cls()

        # Collect the output from make with debug flags
        output = run_make_with_debug_shell(makefile, targets)

        # Check, if the output can be translated properly
        check_debugshell_and_makefile(output.decode("utf-8"))

        # Translate all the commands
        cmds = translate_to_commands(output.decode("utf-8"))

        # store relevant information for later commands
        # for cmd in cmds:
        #     new.register(cmd)

        # and store the translated commands
        # for cmd in cmds:
        #     transformed = new.transform(cmd)
        #     print("New transformed\n")
        #     print(transformed.bashcmd)
        #     if transformed:
        #         new.cmds.append(cmd)
        #     else:
        #         print("blah\n")

        for cmd in cmds:
            transformed_cmd = new.transform(cmd)
            print("Transformed command")
            print(cmd.bashcmd + " in dir " + cmd.curdir)
            print(transformed_cmd.bashcmd + " in dir " + transformed_cmd.curdir)
            new.cmds.append(transformed_cmd)
            new.register(transformed_cmd)

        # for cmd in new.cmds:
        #     new.register(cmd)
        # new.cmds = [new.transform(cmd) for cmd in cmds]

        return new

    def __str__(self):
        """ Print the stored command as a sh-script """
        return linesep.join([str(cmd) for cmd in self.cmds])

    def execute_cmds(self, keep_going=False):
        """
        Execute all the transformed commands.
        Hopefully this results in a full llvm-build
        """

        # filter all commands with no effects
        # cmds = []
        # for cmd in self.cmds:
        #     if not cmd:
        #         print("Null command")
        #         continue
        #     print("Command here " + cmd.bashcmd)
        #     if cmd.has_effects():
        #         cmds.append(cmd)

        #cmds = (cmd for cmd in self.cmds if cmd and cmd.has_effects())

        for cmd in self.cmds:
            if not cmd or not cmd.has_effects():
                #print("Skip command with no effect " + cmd.bashcmd)
                continue
            #print("Command here " + cmd.bashcmd)
            # Execute the commands
            code = cmd.execute()

            # Stop on the first error
            if code != 0:
                if keep_going:
                    print("Execution failed for '%s'" % cmd, file=stderr)
                else:
                    raise OSError("Execution failed for '%s'" % cmd)

    def append_cmd(self, cmd):
        """ Append a command to the internal command storage """

        # register the information of the command
        self.register(cmd)

        # and store the transformed command
        self.cmds.append(self.transform(cmd))

    def append_cmdlist(self, cmds):
        """
        Append all commands from the sequence in the same order
        to the internal command storage
        """

        # register the information of the commands
        for cmd in cmds:
            self.register(cmd)

        # and store all the transformed commands
        self.cmds.extend([self.transform(cmd) for cmd in cmds])
