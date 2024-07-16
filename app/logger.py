import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        original_message = super().format(record)

        before = "\n\n\n\n===================\n"
        after = "\n===================\n\n\n\n"
        formatted_message = f"{before}{original_message}{after}"

        return formatted_message


custom_formatter = CustomFormatter(
    "%(asctime)s - %(name)s - %(levelname)s:\n%(message)s"
)

logger = logging.getLogger("my_logger")
logger.setLevel(logging.DEBUG)
# logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(custom_formatter)

logger.addHandler(console_handler)
