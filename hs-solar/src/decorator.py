from functools import wraps
import time
import logging


def rate_limiter(calls, period):
    call_times = []

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            nonlocal call_times
            now = time.time()

            # Remove timestamps older than `period`
            call_times[:] = [t for t in call_times if now - t < period]

            if len(call_times) >= calls:
                sleep_time = period - (now - call_times[0])
                if sleep_time > 0:
                    logging.info(f"Rate limit exceeded. Sleeping for {sleep_time:.2f} seconds.")
                    time.sleep(sleep_time)
                now = time.time()
                # Clean again after sleeping
                call_times[:] = [t for t in call_times if now - t < period]

            call_times.append(now)
            return f(*args, **kwargs)

        return wrapper

    return decorator
