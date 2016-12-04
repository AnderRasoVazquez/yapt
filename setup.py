from distutils.core import setup

setup(name='yapt',
      version='1.1',
      py_modules=['yapt.confighandler', 'yapt.wrapper', 'yapt.__main__'],
      scripts=['bin/yapt'],
      url='https://github.com/AnderRasoVazquez/yapt',
      download_url='https://github.com/AnderRasoVazquez/yapt/archive/v1.1.tar.gz',
      author='Ander Raso',
      author_email='anderraso@gmail.com',
      license='gplv3',
      long_description='Creates an installation menu around "apt search" command',
      description='Creates an installation menu around "apt search" command',
      summary='Creates an installation menu around "apt search" command',
      )
