from .debianrepochecker import DebianRepoChecker
from .rotatingurlchecker import RotatingURLChecker
from .scrapechecker import ScrapeChecker
from .urlchecker import URLChecker


ALL_CHECKERS = [
    DebianRepoChecker,
    RotatingURLChecker,
    ScrapeChecker,
    URLChecker,
]
