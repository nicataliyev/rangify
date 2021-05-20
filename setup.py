from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

classifiers = [
  'Intended Audience :: Education',
  'Operating System :: OS Independent',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3.9',
  'Programming Language :: Python :: 3.8',
  'Programming Language :: Python :: 3'
]

setup(
    name='rangify',
    version='0.0.5',
    description='cisco interface rangifier',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Nijat Aliyev',
    author_email='nicataliyev@gmail.com',
    classifiers=classifiers,
    py_modules=['rangify', 'helpers'],
    package_dir={'': 'rangify'},
    install_requires=['deepdiff']
)