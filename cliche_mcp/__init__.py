from cliche_mcp.__about__ import __version__
from cliche_mcp.server import mcp

__all__ = ["__version__"]


def main():
    mcp.run()
