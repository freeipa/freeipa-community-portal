# Authors:
#   Drew Erny <derny@redhat.com>
#
# Copyright (C) 2015  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or modify
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

from setuptools import setup



setup(name='freeipa_community_portal',
      version='0.2',
      description='A web application for FreeIPA in a community setting',
      author='Drew Erny',
      author_email='derny@redhat.com',
      license='GPLv3',
      packages=[
          'freeipa_community_portal',
          'freeipa_community_portal.model',
          'freeipa_community_portal.mailers',
      ],
      zip_safe=False
      )
