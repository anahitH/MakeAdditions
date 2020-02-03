"""
MPI linker
"""

from os import path
from ..Transformer import TransformerLlvm
from ...config import LLVMLINK
from ...config import LLVMAR
from ...constants import OPTIMIZERFLAGS, EXECFILEEXTENSION
from ...helper import no_duplicates
import filecmp

class TransformMPICCCLink(TransformerLlvm):
    """ transform link commands """

    @staticmethod
    def can_be_applied_on(cmd):
        result = (cmd.bashcmd.startswith("/usr/bin/mpicc") and
            " -c " not in cmd.bashcmd and
            "-o /dev/null" not in cmd.bashcmd and
            ".c " not in cmd.bashcmd and not cmd.bashcmd.endswith(".c"))
        return result

    @staticmethod
    def apply_transformation_on(cmd, container):
        #print("Tranform cc_link " + cmd.bashcmd)
        # tokenize and remove the original command
        tokens = cmd.bashcmd.split()[1:]
        target = None
        # remove optimizer flags
        tokens = [t for t in tokens if t not in OPTIMIZERFLAGS]

        if "-o" in tokens:
            # append .bc to the output file
            pos = tokens.index("-o")
            # add marker for executable files e.i. files that are not .so
            if ".so" not in tokens[pos + 1]:
                tokens[pos + 1] += EXECFILEEXTENSION
            tokens[pos + 1] += ".bc"
            target = tokens[pos + 1]

        # replace -l flags, if the library was llvm-compiled earlier
        tokens = [
            container.libs.get("lib" + t[2:], t)
            if t.startswith("-l") else t
            for t in tokens]

        # replace references to static libraries
        tokens = [
            container.libs.get(path.basename(t[:-2]), t)
            if t.endswith(".a") else t
            for t in tokens]

        # transform all linked .o-files to the corresponding .bc-file
        tokens = [t[:-2] + ".bc" if t.endswith(".o") else t for t in tokens]

        # filter all command line options except -o
        flagstarts = ["-", "'-", '"-']
        tokens = [t for t in tokens if not (
            any(t.startswith(start) for start in flagstarts)) or t == "-o"]

        new_tokens = []
        for dep in tokens:
            new_tokens.append(dep)
            if not dep.endswith(".bc"):
                continue
            #print("Check dependencies for " + dep)
            for token in tokens:
                if dep == token or not token.endswith(".bc"):
                    continue
                #print("lib " + token)
                #print("     Look with " + path.basename(token))
                dependencies = container.lib_deps.get(path.basename(token))
                if dependencies is None:
                    #print("     Look with " + path.basename(token[:-3]))
                    dependencies = container.lib_deps.get(path.basename(token[:-3]))
                if dependencies is None:
                    #print(" No dependency")
                    continue
                #print("has dependency")
                #print(dependencies)
                for token_dep in dependencies:
                    if dep == token_dep:
                        #print("Remove deps")
                        if dep in new_tokens:
                            new_tokens.remove(dep)
                            break
                    try:
                        cmp = filecmp.cmp(cmd.curdir + "/" + dep, cmd.curdir + "/" + token_dep)
                        if cmp:
                            #print("remove deps")
                            new_tokens.remove(dep)
                            break
                        # else:
                        #     print("Are not equal " + dep + "  " + token_dep)
                    except Exception as ex:
                        #print("can not compare files")
                        #print(ex)
                        continue

        #[print("New token " + new_t) for new_t in new_tokens]
        if "shared" in cmd.bashcmd or "-rdynamic" in cmd.bashcmd:
            if "-o" in new_tokens:
                # append .bc to the output file
                pos = new_tokens.index("-o")
                new_tokens[pos] = ""
            print("Transformed cc to ar!!!")
            if target is None:
                print("Senc vonc klini aranc target")
                cmd.bashcmd = LLVMAR + " qc " + " ".join(no_duplicates(new_tokens))
            else:
                print("bobobo")
                new_tokens.remove(target)
                cmd.bashcmd = LLVMAR + " qc " + target + " " + " ".join(no_duplicates(new_tokens))
        else:
            cmd.bashcmd = LLVMLINK + " " + " ".join(no_duplicates(new_tokens))
        return cmd
