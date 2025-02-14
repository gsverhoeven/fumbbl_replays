from setuptools import setup

setup(name='fumbbl_replays',
      version='0.0.1',
      description='Utility package to plot Fantasy Football board positions and analyze FUMBBL game logs.',
      url='https://github.com/gsverhoeven/fumbbl_replays',
      author='Gertjan Verhoeven',
      packages=['fumbbl_replays'],
      author_email='gertjan.verhoeven@gmail.com',
      license='MIT License',
      install_requires=['pandas', 'requests', 'pillow'],
)


