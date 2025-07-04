# Logging Utility

This repository contains a utility module for consistent logging across various parts of an application. It provides a JSON-style logging mechanism with additional timing metadata and options for log retention, making it easier to inspect or export logs later.

## Contents

- **logs.py**: The main module that implements the logging utilities.

## Overview

The logging utility is designed to enhance the logging experience by:
- Standardizing log formats to JSON.
- Including timing information for each log entry.
- Allowing logs to be retained in memory for later access.

### Key Components

1. **CustomFilter**: A logging filter that formats log records with contextual metadata such as timestamps, time deltas, and additional information for specific log levels (DEBUG, ERROR, CRITICAL).
   - **Methods**:
     - `format_time`: Formats the log record's timestamp.
     - `filter`: Injects metadata into the log record and reformats the message.

2. **RetainHandler**: A custom logging handler that captures formatted log records in memory.
   - **Methods**:
     - `emit`: Stores a formatted log message.
     - `get_retained`: Returns a copy of all retained log messages.
     - `clear_retained`: Clears all retained log messages.

3. **get_logger**: A function to initialize a logger with consistent settings, including optional log retention.
   - **Parameters**:
     - `logger_name`: Name of the logger (default is "BFHTW").
     - `logfile`: Optional log file path; if not provided, logs to stdout.
     - `loglevel`: Sets the logging level (default is "INFO").
     - `logformat`: Specifies the format of the logs (default is "json").
     - `retain_logs`: If True, enables log retention in memory.
     - `force`: If True, forces reinitialization of the logger.

### Usage Example

To use the logging utility, you can call the `get_logger` function:

```python
import logs

logger = logs.get_logger(loglevel='DEBUG', retain_logs=True)
logger.debug(json.dumps({'event': 'test_event', 'status': 'success'}))

# Retrieve retained logs
retained_logs = logger.get_retained()
print(retained_logs)
```

## Conclusion

This logging utility is designed to simplify and standardize logging across applications, making it easier to track events and diagnose issues with detailed and structured log output.