
import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        original_message = super().format(record)

        blank_lines = "\n\n\n\n"
        formatted_message = f"{blank_lines}{original_message}{blank_lines}"

        return formatted_message


custom_formatter = CustomFormatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(custom_formatter)

logger.addHandler(console_handler)

logger.debug("This is a debug message.")
# logger.info("This is an info message.")
# logger.warning("This is a warning message.")
# logger.error("This is an error message.")
# logger.critical("This is a critical message.")
