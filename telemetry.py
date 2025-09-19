# telemetry.py
import logging, sys, time, uuid, contextvars
try:
    from pythonjsonlogger import jsonlogger
except Exception:
    jsonlogger = None

# Context so you can attach run_id/thread_id to every log
run_id_var = contextvars.ContextVar("run_id", default=None)
thread_id_var = contextvars.ContextVar("thread_id", default=None)

def init_logging(level: str = "INFO", to_file: str | None = None):
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.setLevel(level)

    fmt_fields = "%(asctime)s %(levelname)s %(name)s %(message)s"
    if jsonlogger:
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(fmt_fields)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    if to_file:
        fh = logging.FileHandler(to_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

def start_run(run_id: str | None = None, thread_id: str | None = None):
    if run_id is None:
        run_id = str(uuid.uuid4())
    run_id_var.set(run_id)
    if thread_id:
        thread_id_var.set(thread_id)
    logging.getLogger("telemetry").info(
        "run_start",
        extra={"run_id": run_id, "thread_id": thread_id}
    )
    return run_id

def end_run(status: str = "ok", **kw):
    logging.getLogger("telemetry").info(
        "run_end", extra={"run_id": run_id_var.get(), "thread_id": thread_id_var.get(), "status": status, **kw}
    )

def with_telemetry(fn):
    """Decorator to time calls and log errors."""
    import functools
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        log = logging.getLogger(f"tool.{fn.__name__}")
        t0 = time.perf_counter()
        try:
            out = fn(*args, **kwargs)
            dt = time.perf_counter() - t0
            log.info(
                "ok",
                extra={
                    "run_id": run_id_var.get(),
                    "thread_id": thread_id_var.get(),
                    "duration_ms": round(dt*1000, 1),
                    "args": _safe_repr(args),
                    "kwargs": _safe_repr(kwargs) }
            )
            return out
        except Exception as e:
            dt = time.perf_counter() - t0
            log.exception(
                "error",
                extra={
                    "run_id": run_id_var.get(),
                    "thread_id": thread_id_var.get(),
                    "duration_ms": round(dt*1000, 1),
                    "error": repr(e)}
            )
            raise
    return wrapper

def _safe_repr(x):
    """Avoid dumping huge or sensitive values."""
    try:
        s = repr(x)
        return (s[:400] + "...") if len(s) > 400 else s
    except Exception:
        return "<unrepr>"
