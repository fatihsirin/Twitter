import dotenv
import os
from pathlib import Path
current_dir = Path(__file__).parent.absolute()
env = current_dir.joinpath(".env")


def load_env_variable(key, default_value=None, none_allowed=False):
    v = os.getenv(key, default=default_value)
    if v is None and not none_allowed:
        raise RuntimeError(f"{key} returned {v} but this is not allowed!")
    if v == "":
        v = None
    return v


def get_username():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("USERNAME", none_allowed=True)

def get_password():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("PASSWORD", none_allowed=True)

def get_words():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("WORDS", none_allowed=True)

def get_until():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("UNTIL", none_allowed=True)

def get_since():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("SINCE", none_allowed=True)

def get_interval():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("INTERVAL", none_allowed=True)

def get_lang():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("LANG", none_allowed=True)

def get_headless():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("HEADLESS", none_allowed=True)

def get_limit():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("LIMIT", none_allowed=True)

def get_display_type():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("DISPLAY_TYPE", none_allowed=True)

def get_from_account():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("FROM_ACCOUNT", none_allowed=True)

def get_to_account():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("TO_ACCOUNT", none_allowed=True)

def get_mention_account():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("MENTION_ACCOUNT", none_allowed=True)

def get_hashtag():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("HASHTAG", none_allowed=True)

def get_proxy():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("PROXY", none_allowed=True)

def get_proximity():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("PROXIMITY", none_allowed=True)

def get_geocode():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("GEOCODE", none_allowed=True)

def get_minreplies():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("MINREPLIES", none_allowed=True)

def get_minlikes():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("MINLIKES", none_allowed=True)

def get_minretweets():
    dotenv.load_dotenv(env, verbose=True)
    return load_env_variable("MINRETWEETS", none_allowed=True)
