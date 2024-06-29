from threading import Thread


def thread_it(fn):
    def _thread(*args, thread_it: bool = False, **kw):
        if not thread_it:
            return fn(*args, **kw)
        t = Thread(
            target=fn,
            args=args,
            kwargs=kw,
        )
        t.start()
        return t

    return _thread