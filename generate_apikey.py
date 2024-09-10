# -*- coding: utf-8 -*-
"""
This script is used to generate an API key for the user.
"""

from libs import utils
import typer

# Instantiate the typer library
app = typer.Typer()


# define the function for the command line
@app.command()
def main(pwd: str):
    print(utils.encode(pwd))


# ----------------------------------------------------------------
# Main
# ----------------------------------------------------------------
if __name__ == "__main__":
    app()
