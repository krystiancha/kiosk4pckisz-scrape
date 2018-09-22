from logging import INFO, basicConfig

from kiosk4pckisz_scrape.lambda_function import lambda_handler

basicConfig(level=INFO)
print(lambda_handler())
