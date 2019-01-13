"""
cd - change the working directory
"""

from ..Transformer import TransformerLlvm
from ...constants import MAKEANNOTATIONHINT


class TransformMv(TransformerLlvm):
    """ transform mv commands """

    @staticmethod
    def can_be_applied_on(cmd):
        # Keep only makefile cd commands
        return cmd.bashcmd.startswith("mv ")

    @staticmethod
    def apply_transformation_on(cmd, container):
        # extract a list of files to be deleted
        files = cmd.bashcmd.split()[1:]
        new = []
        for file in files:
            embrace = ""
            if file.endswith(".o"):
                new.append(embrace + file[:-2] + ".bc" + embrace)
            else:
                new.append(embrace + file + embrace)

        cmd.bashcmd = "mv " + " ".join(new) if new else ""
        return cmd
