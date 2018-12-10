# -*- coding: utf8 -*-
########################################################################################
# This file is part of exhale.  Copyright (c) 2017-2018, Stephen McDowell.             #
# Full BSD 3-Clause license available here:                                            #
#                                                                                      #
#                https://github.com/svenevs/exhale/blob/master/LICENSE                 #
########################################################################################
"""
Provides fixtures to be available for all test cases.
"""
from __future__ import unicode_literals
import codecs
import os

from exhale import deploy
import pytest


@pytest.fixture(scope="class")
def no_run():
    """
    Disable :func:`exhale.deploy.explode` using a class-level ``pytest`` `fixture`__.

    __ https://docs.pytest.org/en/latest/fixture.html

    The fixture will temporarily assign ``lambda: None`` to ``deploy.explode``,
    restoring the original function after the test case has completed.  A class-scoped
    fixture is used so that this fixture is generated **before** others.

    .. See :func:`pytest:_pytest.FixtureManager.getfixtureclosure`.

    Search for ``def getfixtureclosure`` on `this page`__.

    __ https://docs.pytest.org/en/latest/_modules/_pytest/fixtures.html
    """
    explode = deploy.explode
    deploy.explode = lambda: None
    yield
    deploy.explode = explode


@pytest.fixture(scope="function")
def with_file(path, contents):
    """
    Create a file for a given test function.

    The filename described by ``path`` is created with contents specified by
    ``contents`` before the ``yield``, and deleted after the test runs.

    **Parameters**

    ``path`` (:class:`python:str`)
        The **absolute** path name to create the file with ``contents``.  The parent
        directories of the file in question are **assumed** to already exist.

    ``contents`` (:class:`python:str`)
        The contents of the file to create at ``path``.
    """
    # Create the desired Doxyfile for this test case.
    try:
        with codecs.open(path, "w", "utf-8") as doxyfile:
            doxyfile.write(contents)
    except Exception as e:
        raise RuntimeError(
            "with_doxyfile: unable to create {path}:\n{e}".format(path, e)
        )

    # Let the test run
    yield

    # Now that the test is finished, remove the created Doxyfile.
    try:
        os.remove(path)
    except Exception as e:
        raise RuntimeError(
            "with_doxyfile: unable to remove {path}: {e}".format(path, e)
        )
