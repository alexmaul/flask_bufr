#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author(s):
#
#   Alexander Maul <alexander.maul@dwd.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""
from setuptools import setup

setup(name="trollbufr_flask",
      version="0.1",
      description="Simple online BUFR decoder",
      author="Alexander Maul",
      author_email="alexander.maul@dwd.de",
      packages=["trollbufr_flask"],
      package_data={"trollbufr_flask": ["templates/*.html", "tables/*"]},
      include_package_data=True,
      python_requires=">=2.6, <3",
      )