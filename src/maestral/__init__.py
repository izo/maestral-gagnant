import warnings

__version__ = "1.9.7.dev0"
__author__ = "izo"
__url__ = "https://github.com/izo/maestral-gagnant"


# suppress Python 3.9 warning from rubicon-objc
warnings.filterwarnings("ignore", module="rubicon", category=UserWarning)
