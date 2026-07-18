
from enum import Flag, auto
from os import environ


class EnvGetNumberRestriction(Flag):
    NONE = 0
    ZERO = auto()
    POSITIVE = auto()
    NEGATIVE = auto()


def env_get_bool(key: str, default: bool = False) -> bool:
    if len(key) == 0:
        return default

    env_value = str(environ.get(key, '')).lower().strip()

    if default and env_value == 'false':
        return False

    if not default and env_value == 'true':
        return True

    return default


def env_get_str(key: str, default: str = '') -> str:
    if len(key) == 0:
        return default

    return str(environ.get(key, default))


def env_get_int(key: str, default: int, restrict: EnvGetNumberRestriction = EnvGetNumberRestriction.NONE) -> int:
    if len(key) == 0:
        return default

    env_raw = str(environ.get(key, default)).strip()

    if len(env_raw) == 0:
        return default

    if env_raw[0] in ['+', '-'] and env_raw[1:].isdigit():
        env_int = int(env_raw[1:])

        if env_raw[0] == '-':
            env_int *= -1

    elif env_raw.isdigit():
        env_int = int(env_raw)

    else:
        env_int = default

    if restrict == EnvGetNumberRestriction.NONE:
        return env_int

    if (
        (EnvGetNumberRestriction.ZERO in restrict and env_int == 0)
        or (EnvGetNumberRestriction.POSITIVE in restrict and env_int > 0)
        or (EnvGetNumberRestriction.NEGATIVE in restrict and env_int < 0)
    ):
        return env_int

    return default
