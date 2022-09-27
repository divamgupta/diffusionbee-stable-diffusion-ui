import threading
import queue
import sys
import platform
import select


if platform.system() == "Windows":

    # Due to limitations of windows, we spawn a new thread for stdin. The thread collects the stdin inputs and appends them in list. 

    input_queue = queue.Queue()
    evt = threading.Event()
    print("starting the input thread!")

    def input_collector_worker(input_queue):
        while True:
            input_queue.put(input())
            evt.set()

    input_thread = threading.Thread(
        target=input_collector_worker, args=(
            input_queue,))
    input_thread.daemon = True
    input_thread.start()

    def is_avail():
        """To check in a non blocking way if there is some input available.
        Returns:
            bool: If input is avaialble
        """
        return not input_queue.empty()

    def get_input():
        """To get the input in a blocking way.
        Returns:
            str: The input
        """
        evt.clear()

        if is_avail():
            return input_queue.get()

        evt.wait()

        assert is_avail()
        return get_input()


else:

    # for unix we use select to see if stdin is there or not

    print("non threaded input for unix systems!")

    def get_input():
        return input()

    def is_avail():
        if select.select([sys.stdin, ], [], [], 0.0)[0]:
            return True
        else:
            return False
