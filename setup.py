from setuptools import setup

VERSION = 0.9

setup(
    name="builder",
    version=VERSION,
    license="Apache License 2.0",
    author="The Home Assistant Authors",
    author_email="hello@home-assistant.io",
    url="https://home-assistant.io/",
    description="Hass.io wheels builder form Home Assistant.",
    long_description="",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Home Automation"
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
    ],
    keywords=["docker", "home-assistant", "hass.io"],
    zip_safe=False,
    platforms="any",
    packages=["builder", "builder.upload"],
    include_package_data=True,
)
