=========================================
 OBS service for downloading git tarballs
=========================================

.. image:: https://travis-ci.org/openSUSE/obs-service-git_tarballs.png
   :target: https://travis-ci.org/openSUSE/obs-service-git_tarballs

This is an `Open Build Service`_ source service. It downloads a tarball and parses its git ChangeLog file for information about recent changes which then go to the package's .changes file.

The ``Version`` field will be set to
``%(tarball_version)s+git.%(timestamp)s.%(commit_sha)s``. Where
``tarball_version`` is the version as read from the parent directory
inside the downloaded tarball - everything after the last dash (``-``)
in the directory's name. ``timestamp`` is the current seconds from the
UNIX epoch when the source service was run (if there were new
changes). ``commit_sha`` is the latest commit sha hash from the
ChangeLog file.

The ``git_tarballs`` service will also change the specfile's ``Source:``
to the ``filename`` argument of the service and the ``%setup -q`` line
to match the parent folder name in the tarball.

On the first run, ``git_tarballs`` will just set the spec file's
``Version`` field to the latest git commit. The .changes file will only
be updated with commit message information when newer commits (compared
to the one now set in ``Version``) are found.

Dependencies
------------

Up to date requirements are kept in the files ``requirements.txt`` and
``test-requirements.txt``

Contributing
------------
This is the git repository for `openSUSE\:Tools/obs-service-git_tarballs`_. The authoritative source is https://github.com/openSUSE/obs-service-git_tarballs.

You can submit or ask for improvements using github's Pull Requests or Issues. If you're sending a patch, please make sure the testsuite is still running and also run flake8 on the files you've modified. It would be great if you could also modify this README file to describe new functionality and add tests.

You can take a look at the .travis.yml file to see how the testsuite and flake8 are being run.


.. _Open Build Service: http://openbuildservice.org/
.. _python-mock: http://www.voidspace.org.uk/python/mock/mock.html
.. _openSUSE\:Tools/obs-service-git_tarballs: https://build.opensuse.org/package/show/openSUSE:Tools/obs-service-git_tarballs
