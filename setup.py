import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

REQUIREMENTS = [
    # Add your list of production dependencies here, eg:
    'aiohttp >= 3.8.3',
    'oauthlib >= 3.2.2',
]

DEV_REQUIREMENTS = [
    'black == 22.*',
    'build == 0.7.*',
    'flake8 == 4.*',
    'isort == 5.*',
    'mypy == 0.942',
    'pytest == 7.*',
    'pytest-cov == 4.*',
    'twine == 4.*',
]

setuptools.setup(
    name='carrier-infinity-evolution',
    version='0.0.1',
    description='Carrier Infinity/Evolution Python Client',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/thehesiod/carrier-infinity-evolution',
    author='thehesiod',
    license='Apache',
    packages=setuptools.find_packages(
        exclude=[
            'examples',
            'test',
        ]
    ),
    package_data={
        'carrier-infinity-evolution': [
            'py.typed',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS,
    extras_require={
        'dev': DEV_REQUIREMENTS,
    },
    entry_points={
        'console_scripts': [
            'carrier-infinity-evolution=carrier_infinity_evolution.carrier:main',
        ]
    },
    python_requires='>=3.7, <4',
)
