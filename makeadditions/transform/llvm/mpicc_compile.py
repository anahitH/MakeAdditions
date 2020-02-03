"""
MPI compiler
"""

from ..Transformer import TransformerLlvm
from ...config import CLANG
from ...constants import (
    DEPENDENCYFLAGS,
    DEPENDENCYEMISSION,
    OPTIMIZERFLAGS
)


class TransformMPICCCompile(TransformerLlvm):
    """ transform compile commands """

    @staticmethod
    def can_be_applied_on(cmd):
        return (cmd.bashcmd.startswith("/usr/bin/mpicc") and
                "-o /dev/null" not in cmd.bashcmd and
                " -c " in cmd.bashcmd)

    @staticmethod
    def apply_transformation_on(cmd, container):
        print("Apply transformation on " + cmd.bashcmd)
        # tokenize and remove the original command
        tokens = cmd.bashcmd.split()[1:]

        # remove optimizer flags
        tokens = [t for t in tokens if t not in OPTIMIZERFLAGS]

        # deactivate optimization
        tokens.insert(0, "-O0")

        # remove dependency emission
        #for deptoken in DEPENDENCYEMISSION:
        #    if deptoken in tokens:
        #        pos = tokens.index(deptoken)
        #        del tokens[pos:pos + 2]

        # remove dependency flags
        #tokens = [t for t in tokens if t not in DEPENDENCYFLAGS]

        # build the new command
        newcmd = CLANG + " -emit-llvm "

        # add -g flag, if it was not there before
        if "-g" not in tokens:
            newcmd += "-g "

        # rename the output-file from .o to .bc, if specified
        if "-o" in tokens:
            pos = tokens.index("-o")
            if tokens[pos + 1].endswith(".o"):
                tokens[pos + 1] = tokens[pos + 1][:-2] + ".bc"
            tokens.insert(pos-1, "-I/usr/include/mpi")

        for token in tokens:
            if token.endswith(".o"):
                token = token[:-2]+".bc"

        cmd.bashcmd = newcmd + " ".join(tokens)
        return cmd
