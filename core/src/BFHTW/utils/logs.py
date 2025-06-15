'''
Utils to make logging consistent across all parts of the app.

Provides a JSON-style logging filter with timing metadata and optional
log retention for later inspection or export.
'''

from functools import wraps
import logging
import json
from typing import Callable, List, Optional

import typer

DEFAULT_LOGGER_NAME="BFHTW"

# Mapping between integer and human log levels
LOG_LEVELS_MAP = {
    'NOTSET': 0,
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50 }

# Add extra information when logging at these levels
EXTRA_INFO_LOG_LEVELS = { 10, 40, 50 }

class CustomFilter(logging.Filter):
    '''Format log records with timing and contextual metadata.

    Adds formatted timestamps, time deltas between logs, and contextual
    information like filename and function name for DEBUG, ERROR, or CRITICAL logs.
    '''
    def __init__(
            self,
            loglevel: str,
            *args,
            logformat: Optional[str] = 'json',
            **kwargs ):
        '''Initialise the custom filter with log level and format options.'''
        super(CustomFilter, self).__init__(*args, **kwargs)
        self.logformat = logformat
        self.loglevel = loglevel
        self.previous_delta_ms = self.first_delta_ms = None
        # Create in __init__ so it doesn't create new one for each log
        self.__time_format_func = logging.Formatter().formatTime

    def format_time(self,
        record: logging.LogRecord,
        datefmt: Optional[str] = '%Y-%m-%d %H:%M:%S' ) -> str:
        '''Format record time using the logging.Formatter formatTime function.'''
        return self.__time_format_func(record, datefmt=datefmt)

    def filter(
        self,
        record: logging.LogRecord) -> bool:
        '''Inject metadata and formatting into the log record.'''
        if self.first_delta_ms is None:
            previous_delta_ms = record.relativeCreated
            self.first_delta_ms = record_delta_ms = previous_delta_ms
        else:
            previous_delta_ms = self.previous_delta_ms
            record_delta_ms = record.relativeCreated

        try:
            log_as_dict = json.loads(record.msg.strip())
        except json.JSONDecodeError:
            log_as_dict = { 'message': record.msg.strip() }

        log_as_dict.update({
            'level': record.levelname,
            'time': self.format_time(record),
            'ms_last':  (f'{(float(record_delta_ms) - float(previous_delta_ms)):0.5}'),
            'ms_start': (f'{(float(record_delta_ms) - float(self.first_delta_ms)):0.5}') })

        # output dev-centric info when error, critical or logging at debug level
        if record.levelno in EXTRA_INFO_LOG_LEVELS:
            log_as_dict.update({
                'name': record.name,
                'filename': record.filename,
                'lineno': record.lineno,
                'funcName': record.funcName })

        record.reformatted_msg = json.dumps(log_as_dict)[1:-1]

        self.previous_delta_ms = record_delta_ms

        return True

class RetainHandler(logging.Handler):
    '''Capture and store formatted log records in memory.'''
    def __init__(self) -> None:
        '''Initialise an empty log store.'''
        super().__init__()
        self.records: List[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        '''Store a formatted log message for later retrieval.'''
        self.records.append(
            getattr(record, 'reformatted_msg', record.getMessage()) )

    def get_retained(self) -> List[str]:
        '''Return a copy of all retained log messages.'''
        return self.records.copy()

    def clear_retained(self) -> None:
        '''Clear all retained log messages.'''
        self.records.clear()

def get_logger(
    logger_name: Optional[str] = DEFAULT_LOGGER_NAME,
    logfile: Optional[str] = None,
    loglevel: Optional[str] = 'INFO',
    logformat: Optional[str] = 'json',
    retain_logs: Optional[bool] = False,
    force: Optional[bool] = False ) -> logging.Logger:
    '''Initialise a logger with consistent filters and optional log retention.

    Adds a formatter that emits JSON-style log records with timestamps and timing
    deltas. When `retain_logs=True`, attaches a handler that stores logs in memory
    and exposes `get_retained()` and `clear_retained()` on the logger instance.
    '''
    # Grab the logger and return immediately if already initialised
    L = logging.getLogger(logger_name)
    if not force and hasattr(L, 'initialised'):
        return L

    # Set logfile or stdout
    if logfile is None:
        lh = logging.StreamHandler()
    else:
        lh = logging.FileHandler(logfile)

    setattr(L, 'logformat', logformat)

    # Set log level
    lh.setLevel(loglevel)
    L.setLevel(LOG_LEVELS_MAP.get(loglevel, 0))

    # Add custom filter and formatter.
    # Note that the formatter uses: "reformatted_msg" --> set in CustomFilter.filter
    lh.setFormatter(logging.Formatter(fmt='{%(reformatted_msg)s}'))
    lh.addFilter(CustomFilter(loglevel, logformat=logformat))

    # Remove any existing handlers and subsitute the new one in instead
    for handler in list(L.handlers):
        L.removeHandler(handler)
    L.addHandler(lh)

    # Conditionally add the retain handler
    if retain_logs:
        retain_handler = RetainHandler()
        retain_handler.setLevel(loglevel)
        L.addHandler(retain_handler)

        # Monkey-patch onto logger
        setattr(L, 'get_retained', retain_handler.get_retained)
        setattr(L, 'clear_retained', retain_handler.clear_retained)
    else:
        # Dummy methods if not retaining
        setattr(L, 'get_retained', lambda: [])
        setattr(L, 'clear_retained', lambda: None)

    # Set this no so that future calls skip the initialisation
    setattr(L, 'initialised', True)
    return L
