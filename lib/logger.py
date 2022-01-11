import logging
import os
import sys

filename = "./lib/myapp.txt"
filename = os.path.dirname(__file__) + "/myapp.txt"
LogFormat = '%(asctime)s %(levelname)s %(message)s'


def init_log(level=logging.INFO):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    # make log file directory when not exist

    if logging.root:
        del logging.root.handlers[:]
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=level,
                        format=LogFormat,
                        datefmt='%Y-%m-%d %H:%M',
                        filename=filename,
                        filemode='a',
                        # force=True
                        )

    logger = logging.getLogger()

    logFormatter = logging.Formatter(LogFormat)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logFormatter)
    logger.addHandler(ch)


    return logger


logger = init_log()
logger.info("zaa")
