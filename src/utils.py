from threading import Thread


def thread_it(fn):
    def _thread(*args, thread_it: bool = False, **kw):
        if not thread_it:
            return fn(*args, **kw)
        t = Thread(
            target=fn,
            args=args,
            kwargs=kw,
            daemon=True,
        )
        t.start()
        return t

    return _thread

class Command:
    def __init__(self, *commands: str) -> None:
        self.commands: list[str] = list(commands)

    def __iter__(self):
        return self.commands.__iter__()

    def add_command(self, command: str, value: str):
        if value is not None:
            self.commands += [command, value]
        return self

    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name[0] == "_":
                name = name[1:]
            return lambda value: self.add_command(command=f"-{name}", value=value)
