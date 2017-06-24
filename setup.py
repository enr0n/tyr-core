from setuptools import setup

setup(name='tyr',
      version='1.0',
      description='lightweight build-and-test server',
      url='',
      author='Nick Rosbrook',
      author_email='nrosbrook@mail.smcvt.edu',
      license='MIT',
      packages=['tyr'],
      entry_points = {
          'console_scripts': ['tyr-server=tyr.command_line:main'],
      },
      install_requires=[
          'ConfigParser',
          'PyDispatcher',
          'paramiko',
      ],
      zip_safe=False)
