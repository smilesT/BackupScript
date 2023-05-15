#!/bin/bash

# Check if Python is installed
if
    ! command -v python3 &
    >/dev/null
then
    echo "Python 3 could not be found. Please install Python 3 and try again."
    exit
fi

# Check if Poetry is installed, and install it if not
if
    ! command -v poetry &
    >/dev/null
then
    echo "Poetry could not be found. Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install project dependencies and build the project
echo "Installing project dependencies and building the project..."
poetry install
poetry build

# Find the .whl file
WHL_FILE=$(find dist -name "*.whl" | head -n 1)

if [ -z "$WHL_FILE" ]; then
    echo "No .whl file found in dist/ directory."
    exit 1
fi

# Move the built project to /usr/bin
echo "Moving the built project to /usr/bin..."
pip install $WHL_FILE

echo "Installation complete."
