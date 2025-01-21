from setuptools import setup, find_packages
from codecs import open
from os import path

__version__ = '1.0.9'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open('README-en.md', encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='image-downloader-ml',
    version=__version__,
    description="Image download tools used in machine learning, deep learning.",
    long_description=long_description,
    url='https://github.com/2635064692/image-downloader',
    download_url='https://github.com/2635064692/image-downloader/releases/download/' + __version__+'/image_downloader_ml-'+__version__+'.tar.gz',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='google bing baidu images download image-dataset terminal command-line',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Hai Zh',
    install_requires=install_requires,
    dependency_links=dependency_links,
    long_description_content_type='text/markdown',
    author_email='peterzh1998@gmail.com',
    entry_points={
        'console_scripts': [
            'image-downloader-ml = downloader.ImageDownloader:main'
        ]},
)
