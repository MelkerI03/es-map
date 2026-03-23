from multiprocessing import Process

import uvicorn


def run_api(app, host="127.0.0.1", port=8000):
    """Run FastAPI app in a separate process."""

    proc = Process(
        target=uvicorn.run,
        args=(app,),
        kwargs={
            "host": host,
            "port": port,
            "log_level": "info",
        },
        daemon=True,
    )

    proc.start()
    return proc
