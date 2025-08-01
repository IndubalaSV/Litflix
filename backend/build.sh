#!/usr/bin/env bash
# Custom build script for Render

# Use Python version from runtime.txt
pyenv install --skip-existing "$(cat runtime.txt)"
pyenv global "$(cat runtime.txt)"


# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
