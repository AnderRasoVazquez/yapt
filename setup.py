from distutils.core import setup, Extension

setup(name='yapt',
      version='1.0',
      py_modules=['yapt.confighandler', 'yapt.wrapper', 'yapt.__main__'],
      scripts=['bin/yapt'],
      url='https://github.com/AnderRasoVazquez/yapt',
      author='Ander Raso',
      author_email='anderraso@gmail.com',
      license='gplv3',
      long_description='Creates an installation menu around "apt search" command',
      )
