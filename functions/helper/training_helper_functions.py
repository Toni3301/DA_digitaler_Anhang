import contextlib
import os
import sys


def silent_log_message(component, instanceName, status, category, message):
    """remove log messages"""
    try:
        msg = message.decode("latin-1")
        print("[%s] %s" % (category, msg))
    except:
        pass


@contextlib.contextmanager
def suppress_fmu_output_context():
    """Unterdrückt FMU/Dymola-Ausgaben."""
    saved_stdout = sys.stdout
    saved_stderr = sys.stderr
    try:
        with open(os.devnull, 'w') as fnull:
            sys.stdout = fnull
            sys.stderr = fnull
            yield
    finally:
        sys.stdout = saved_stdout
        sys.stderr = saved_stderr

