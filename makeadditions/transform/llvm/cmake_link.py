"""
ar - create, modify, and extract from archives
"""

import re

from makeadditions.transform import directory
from ..Transformer import TransformerLlvm
from makeadditions.Command import Command


class TransformCmakeLink(TransformerLlvm):
    """ transform ar commands """
    cmd_prefixes = ["/usr/bin/cmake -E cmake_link_script ", "/usr/local/bin/cmake -E cmake_link_script "]

    @staticmethod
    def can_be_applied_on(cmd):
        return any(cmd.bashcmd.startswith(s) for s in TransformCmakeLink.cmd_prefixes)

    @staticmethod
    def apply_transformation_on(cmd, container):
        print("TransformCmakeLink " + cmd.bashcmd)
        link_file_name = re.split('\\s', cmd.bashcmd)[3]
        link_file = open(cmd.curdir + "/" + link_file_name, 'r')
        link_line = link_file.readline()
        link_cmd = Command(link_line, cmd.curdir)
        relevant = directory.list_all_llvm_transformers()
        for transformer in relevant:
            if transformer is TransformCmakeLink:
                continue
            if transformer.can_be_applied_on(link_cmd):
                transformed_cmd = transformer.apply_transformation_on(link_cmd, container)
                print("Transformed cmake link command " + transformed_cmd.bashcmd)
                return transformed_cmd

        print("Could not transform from cmake file ")
        print(cmd.curdir + "/" + link_file_name)
        print("Command")
        print(link_cmd.bashcmd)
        exit(-1)
        return None
