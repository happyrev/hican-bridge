import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    # Ensure logs directory exists
    log_dir = os.path.join(app.root_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers to prevent duplicate logs in Flask debug mode
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler for development/debugging
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for production/long-term logging
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=1024 * 1024 * 10, # 10 MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(pathname)s:%(lineno)d: %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Optionally, suppress some chatty loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    app.logger.info('Logging configured successfully.')
