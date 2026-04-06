import threading


def run_in_thread(func):
    """
    Decorator to run a function in a separate thread.
    """

    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread  #

    return wrapper
