from setuptools import setup

setup(
    name='verbit-streaming-sdk',
    description="Client SDK for Verbit's Streaming Speech Recognition services",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/verbit-ai/verbit-streaming-python-sdk',

    version='0.10.4',

    packages=['verbit'],
    package_dir={'verbit': 'verbit'},
    python_requires=">=3.8",
    install_requires=[
        'websocket-client~=1.2.3',
        'tenacity<9>8',
        'requests<3'
    ],
    zip_safe=False
)
