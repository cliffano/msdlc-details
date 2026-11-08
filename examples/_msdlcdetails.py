# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring,duplicate-code,too-many-locals
from msdlcdetails import Display

display = Display(conf_file='msdlcdetails.yaml')
text = display.format(reverse=False, transformation='lower')
print(text)