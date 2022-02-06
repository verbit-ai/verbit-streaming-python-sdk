from setuptools import setup

setup(
    name='verbit-streaming-sdk',
    description='',
    long_description='',
    version='0.8.0',

    packages=['verbit'],
    package_dir={'verbit': 'verbit'},
    python_requires=">=3.6",
    install_requires=[
        'websocket-client==1.2.3',
        'tenacity==8.0.1'
    ],
    zip_safe=False
)
