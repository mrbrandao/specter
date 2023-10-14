from setuptools import setup, find_packages

setup(
  name='specter',
  version='0.1.0',
  include_package_data=True,
  install_requires=['click'],
  package_dir={'':'src'},
  #packages=find_packages(),
  packages=['specter'],
  py_modules=['specter'],
  entry_points={
      'console_scripts':['specter=specter.cli:cli'],
      },
  )
