import os
import sys
import subprocess
import uuid


def boot(*args):
    try:
        ret = subprocess.run(args)

        if ret.returncode < 0:
            print("Pipeline step execution was terminated by signal",
                  -(ret.returncode),
                  file=sys.stderr)
        else:
            print("Pipeline step execution returned",
                  ret.returncode,
                  file=sys.stderr)

    except OSError as e:
        print("Execution failed:", e, file=sys.stderr)
        return 1

    return ret.returncode


if __name__ == "__main__":
    entry_script = sys.argv[1]
    sys.exit(boot('Rscript', '--no-site-file', '--no-environ', '--no-restore', entry_script))
