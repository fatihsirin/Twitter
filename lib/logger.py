import logging
import os

filename = "./lib/myapp.txt"
filename = os.path.dirname(__file__) + "/myapp.txt"
print(filename)


def init_log(level=logging.INFO):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # make log file directory when not exist

    if logging.root:
        del logging.root.handlers[:]
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        filename=filename,
                        filemode='a',
                        # force=True
                        )

    logger = logging.getLogger()
    return logger


logger = init_log()
logger.info("zaa")
