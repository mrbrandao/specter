from setuptools import setup, find_packages

setup(
  name='specter',
  version='0.1.0',
  include_package_data=True,
  install_requires=['click>=8.1.7,<=9.0.0',
                    'requests>=2.31.0,<=3.0.0',
                    'rich>=13.6.0'
                    ],
  package_dir={'':'src'},
  packages=['specter'],
  py_modules=['specter'],
  entry_points={
      'console_scripts':['specter=specter.cli:cli'],
      },
  )
