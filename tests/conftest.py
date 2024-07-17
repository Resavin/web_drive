import sys
import os

# To be able to import app from tests
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))
# # To be able to import inside app folder
# sys.path.insert(0, os.path.abspath(
#     os.path.join(os.path.dirname(__file__), '..', "app")))
