import sys
import threading


class KThread(threading.Thread):
    """
    A subclass of threading.Thread with a kill() method.

    This class extends the functionality of the Thread class from the threading module.
    It allows stopping the execution of the thread by raising a SystemExit exception.

    :param args: Variable length argument list.
    :type args: tuple
    :param kwargs: Arbitrary keyword arguments.
    :type kwargs: dict

    :ivar killed: Indicates if the thread has been killed.
    :vartype killed: bool
    """

    def __init__(self, *args, **kwargs):
        """
        Initializes a new instance of the KThread class.

        :param args: Variable length argument list.
        :type args: tuple
        :param kwargs: Arbitrary keyword arguments.
        :type kwargs: dict
        """
        super().__init__(*args, **kwargs)
        self.killed = False

    def start(self):
        """
        Starts the thread and installs the trace.
        """
        self.__run_backup = self.run
        self.run = self.__run
        super().start()

    def __run(self):
        """
        Hacked run function that installs the trace.
        """
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        """
        Function used as a global trace for the thread.

        :param frame: Current stack frame.
        :type frame: frame
        :param why: Reason for the trace event.
        :type why: str
        :param arg: Associated argument.
        :type arg: object

        :return: The localtrace function if the thread is killed and the event is a line event, or None.
        :rtype: function or None
        """
        if why == "call":
            return self.localtrace
        return None

    def localtrace(self, frame, why, arg):
        """
        Function used as a local trace for the thread.

        :param frame: Current stack frame.
        :type frame: frame
        :param why: Reason for the trace event.
        :type why: str
        :param arg: Associated argument.
        :type arg: object

        :return: The localtrace function if the thread is killed and the event is a line event, or None.
        :rtype: function or None
        """
        if self.killed and why == "line":
            raise SystemExit()
        return self.localtrace

    def kill(self):
        """
        Stops the execution of the thread by setting the killed attribute to True.
        """
        self.killed = True
