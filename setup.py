from setuptools import setup, find_packages

with open("readme.md", "r") as rdme:
    long_description = rdme.read()


setup(
    name="NasNas",
    version="0.1.2",
    author="Modar Nasser",
    author_email="modar1999@gmail.com",
    description="A simple game framework to get started quickly with python and sfml.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Madour/pyNasNas",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    keywords=["sfml", "game dev", "game engine", "framework"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: zlib/libpng License",
        "Programming Language :: Python :: 3"
    ]
)
