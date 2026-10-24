"""Cache decorator that works with or without a Streamlit runtime.

Under Streamlit, `@cache_data` behaves exactly like `st.cache_data`. Inside the
FastAPI server, Streamlit is never imported, so the decorator is a no-op and the
plain function runs. This lets data modules such as `lib.yt_data` be shared by
both the Streamlit app and the API.
"""
import sys


def cache_data(*args, **kwargs):
    st = sys.modules.get("streamlit")

    def decorate(fn):
        if st is not None and hasattr(st, "cache_data"):
            try:
                return st.cache_data(*args, **kwargs)(fn)
            except Exception:
                return fn
        return fn

    # Bare use: @cache_data
    if len(args) == 1 and callable(args[0]) and not kwargs:
        return decorate(args[0])
    # Parameterised use: @cache_data(show_spinner=False)
    return decorate


def cache_resource(*args, **kwargs):
    st = sys.modules.get("streamlit")

    def decorate(fn):
        if st is not None and hasattr(st, "cache_resource"):
            try:
                return st.cache_resource(*args, **kwargs)(fn)
            except Exception:
                return fn
        return fn

    if len(args) == 1 and callable(args[0]) and not kwargs:
        return decorate(args[0])
    return decorate
