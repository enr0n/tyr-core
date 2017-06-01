from setuptools import setup

setup(name='tyr',
      version='1.1',
      description='lightweight build-and-test server',
      url='',
      author='Nick Rosbrook',
      author_email='nrosbrook@mail.smcvt.edu',
      license='MIT',
      packages=['tyr'],
      install_requires=[
          'ConfigParser',
          'PyDispatcher',
          'paramiko',
      ],
      zip_safe=False)
