import time
from functions import make_login, driver
from treatments import treat_455, treat_file_455


driver_chr = driver(headless=True)

make_login(driver_chr)
time.sleep(3)


new_file = treat_455(driver_chr)


time.sleep(2)
driver_chr.quit()

treat_file_455(new_file)