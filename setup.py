from setuptools import setup

setup(
    name='mkwheelhouse',
    version='0.3.0',
    author='Nikhil Benesch',
    author_email='benesch@whoop.com',
    py_modules=['mkwheelhouse'],
    url='https://github.com/WhoopInc/mkwheelhouse',
    description='Amazon S3 wheelhouse generator',
    classifiers=[
      'License :: OSI Approved :: MIT License',
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools'
    ],
    install_requires=[
        "awscli >= 1.3.6",
        "yattag >= 0.9.2",
        "wheel >= 0.23.0",
        "pip >= 1.5.4",
    ],
    entry_points={
        'console_scripts': [
            'mkwheelhouse=mkwheelhouse:main'
        ],
    }
)
