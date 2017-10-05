#!/usr/bin/env

import logging,logging.handlers,os

def log(message):
    handler = logging.handlers.WatchedFileHandler(
        os.environ.get("LOGFILE", "/var/log/messages"))
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
    root.addHandler(handler)
    logging.exception("ImageCapture - " + message)
