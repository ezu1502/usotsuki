import time
import functools
from contextlib import ContextDecorator

class TimeCounter(ContextDecorator):
    def __init__(self, *args) -> None:
        self.name = None
        self.function = None

        self._elapsed: float | None = None

        match len(args):
            case 0:
                self.function, self.name = None, None
            case 1:
                self._validate_init_argument(args[0])
            case 2:
                for arg in args:
                    self._validate_init_argument(arg)
            case _:
                raise TypeError(f"TimeCounter() takes 0, 1 or 2 arguments; {len(args)} were given.")

        if self.function is not None:
            functools.update_wrapper(self, self.function) #type: ignore - Não tem como ser str, exceção tratada acima

    def _validate_init_argument(self, arg):
            if callable(arg):
                if self.function is not None:
                    raise TypeError("Only one function is supported at a time!")
                self.function = arg
            elif isinstance(arg, str):
                if self.name is not None:
                    raise TypeError("Only one name is supported at a time!")
                self.name = arg
            else:
                raise TypeError("TimeCounter only supports callable objects or string names!")
            
    #usados quando for usado num with
    def __enter__(self):
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self._end_time = time.perf_counter()
        self._elapsed = self._end_time - self._start_time

        delta_string = f"{round(self._elapsed*1000, 2)}ms" if self._elapsed < 1 else f"{round(self._elapsed, 3)}s"

        if self.name is None:
            if self.function is not None:
                self.name = self.function.__qualname__
                print(f"{self.name} took {delta_string}")
            else:
                print(f"Action took {delta_string}")
        else:
            print(f"{self.name} took {delta_string}")

        return False

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self.__call__, instance)

 

    

    @property
    def elapsed_time(self):
        return self._elapsed

    
    #Usado quando chamado como decorator
    def __call__(self, *args, **kwargs):
        if self.function is None:
            if len(args) != 1 or not callable(args[0]):
                raise TypeError("Expected callable as decorator argument")

            self.function = args[0]
            if self.name is None:
                self.name = self.function.__qualname__
            functools.update_wrapper(self, self.function)
        else:
            with self:
                return self.function(*args, **kwargs)

        return self

    
# TimeCounter(func, "name")
# @TimeCounter
# @TimeCounter()
# @TimeCounter("name")
# with TimeCounter():