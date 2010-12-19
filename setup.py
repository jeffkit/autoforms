#!/usr/bin/env python

from setuptools import setup
from autoforms import version

url="http://autoforms.sandbox.jeffkit.info"

long_description="Autoforms is a custom form engine for django framework .  For more information see " + url

setup(name="autoforms",
      version=version,
      description="Custom form engine for django",
      maintainer="jeff kit",
      maintainer_email="bbmyth@gmail.com",
      url = url,
      long_description=long_description,
      packages=['autoforms']
     )

