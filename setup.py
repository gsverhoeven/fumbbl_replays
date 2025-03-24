from setuptools import setup

setup(name='fumbbl_replays',
      version='0.0.1',
      description='Utility package to plot Fantasy Football board positions and analyze FUMBBL game logs.',
      url='https://github.com/gsverhoeven/fumbbl_replays',
      author='Gertjan Verhoeven',
      author_email='gertjan.verhoeven@gmail.com',
      license='MIT License',
      install_requires=['pandas', 'requests', 'pillow', 'ipykernel', 'openpyxl', 'plotnine'],
      include_package_data=True
)


