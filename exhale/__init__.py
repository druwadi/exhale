# -*- coding: utf8 -*-
########################################################################################
# This file is part of exhale.  Copyright (c) 2017-2018, Stephen McDowell.             #
# Full BSD 3-Clause license available here:                                            #
#                                                                                      #
#                https://github.com/svenevs/exhale/blob/master/LICENSE                 #
########################################################################################

from __future__ import unicode_literals

import six
from sphinx.errors import ConfigError

__version__ = "0.1.8"


def _assert_is_dictionary_with_string_keys(d, title):
    # Make sure it is a dictionary.
    if type(d) is not dict:
        raise ConfigError(
            "`{title}` in `conf.py` must be a dictionary, but was `{got}`.".format(
                title=title,
                got=type(d)
            )
        )

    # Make sure all of the keys are strings (values validated later).
    for key in d:
        if not isinstance(key, six.string_types):
            raise ConfigError(
                "`{title}` had key `{key}` of type `{key_t}`, but only strings are allowed.".format(
                    title=title, key=key, key_t=type(key)
                )
            )


class ExhaleProject(object):
    def __init__(self, config):
        self.app = config.app
        self.project_name = config.project_name
        self.config = config

        self.root = None

    def run_doxygen(self):
        pass

    def parse(self):
        pass

    def explode(self):
        pass

def environment_ready(app):
    # Defer importing configs until sphinx is running.
    from . import configs
    from . import utils
    from . import deploy

    # initial type-safety checks for `exhale_args`
    exhale_args = app.config.exhale_args
    _assert_is_dictionary_with_string_keys(exhale_args, "exhale_args")

    # initial type-safety checks for `exhale_projects`
    exhale_projects = app.config.exhale_projects
    _assert_is_dictionary_with_string_keys(exhale_projects, "exhale_projects")
    for project in exhale_projects:
        _assert_is_dictionary_with_string_keys(
            exhale_projects[project], "exhale_projects['{0}']".format(project)
        )

    # initial type-safety checks for `exhale_global_args`
    exhale_global_args = app.config.exhale_global_args
    _assert_is_dictionary_with_string_keys(exhale_global_args, "exhale_global_args")

    # `exhale_args` implies Exhale can overwrite `exhale_projects`
    if exhale_args and exhale_projects:
        raise ConfigError(
            "`exhale_args` and `exhale_projects` may not both be specified.  "
            "Using `exhale_args` implies a single project."
        )

    # `exhale_args` cannot be used with `exhale_global_args`
    if exhale_args and exhale_global_args:
        raise ConfigError(
            "`exhale_args` and `exhale_global_args` may not both be specified.  "
            "Using `exhale_args` implies a single project."
        )

    # create `exhale_projects` when `exhale_args` is being used
    if exhale_args:
        app.config.exhale_projects = {
            "exhale_auto": {key: value for key, value in exhale_args.items()}
        }
        exhale_projects = app.config.exhale_projects

    # generate each project
    for project_name in exhale_projects:
        config = configs.Config(app, project_name)
        project = ExhaleProject(config)
        project.run_doxygen()
        project.parse()
        project.explode()

    # First, setup the extension and verify all of the configurations.
    configs.apply_sphinx_configurations(app)
    ####### Next, perform any cleanup

    # Generate the full API!
    try:
        deploy.explode()
    except:
        utils.fancyError("Exhale: could not generate reStructuredText documents :/")


def setup(app):
    app.setup_extension("breathe")
    app.add_config_value("exhale_args", {}, "env")
    app.add_config_value("exhale_projects", {}, "env")
    app.add_config_value("exhale_global_args", {}, "env")

    app.connect("builder-inited", environment_ready)

    return {"version": __version__}
