"""
ar - create, modify, and extract from archives
"""

import re
from ..Transformer import TransformerLlvm
from ...config import LLVMAR
from ...config import LLVMLINK


class TransformAr(TransformerLlvm):
    """ transform ar commands """

    @staticmethod
    def can_be_applied_on(cmd):
        result = cmd.bashcmd.startswith("ar ") and \
                 re.search(r"ar [-]?[cruqs]+ [^ ]+\.a", cmd.bashcmd)
        result = result or cmd.bashcmd.startswith("/usr/bin/ar ") and \
                 re.search(r"ar [-]?[qc]+ [^ ]+\.a", cmd.bashcmd)
        return result

    @staticmethod
    def apply_transformation_on(cmd, container):
        # tokenize and remove the original command with first option
        tokens = cmd.bashcmd.split()[1:]

        # llvm needs a flag for specifying the output file
        tokens[0] = "-o"

        # Add .bc file extension to static archive -> libxxx.a.bc
        tokens[1] += ".bc"

        # transform all linked .o-files to the corresponding .bc-file
        tokens = [t[:-2] + ".bc" if t.endswith(".o") else t for t in tokens]

        #cmd.bashcmd = LLVMAR + " " + " ".join(tokens)
        cmd.bashcmd = LLVMLINK + " " + " ".join(tokens)
        return cmd
