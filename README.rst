===============================
Charlesbot Rundeck Plugin
===============================

.. image:: https://img.shields.io/travis/marvinpinto/charlesbot-rundeck/master.svg?style=flat-square
    :target: https://travis-ci.org/marvinpinto/charlesbot-rundeck
    :alt: Travis CI
.. image:: https://img.shields.io/coveralls/marvinpinto/charlesbot-rundeck/master.svg?style=flat-square
    :target: https://coveralls.io/github/marvinpinto/charlesbot-rundeck?branch=master
    :alt: Code Coverage
.. image:: https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square
    :target: LICENSE.txt
    :alt: Software License

A Charlesbot__ plugin to do a really awesome thing!

__ https://github.com/marvinpinto/charlesbot


How does this work
------------------

This plugin adds the following ``!help`` targets:

.. code:: text

    !command - Do a thing!

TODO: Fill in a description about what this plugin does and how it works.
Screenshots are helpful, too!


Installation
------------

.. code:: bash

    pip install charlesbot-rundeck

Instructions for how to run Charlesbot are over at https://github.com/marvinpinto/charlesbot.


Configuration
-------------

In your Charlesbot ``config.yaml``, enable this plugin by adding the following
entry to the ``main`` section:

.. code:: yaml

    main:
      enabled_plugins:
        - 'charlesbot_rundeck.rundeck.Rundeck'

TODO: If there is any more configuration, mention it here.

Rundeck ACL Policy
~~~~~~~~~~~~~~~~~~

Make sure you have a ``apitoken.aclpolicy`` file that looks something like:

.. code:: yaml

    description: API project level access control
    context:
      project: '.*' # all projects
    for:
      # ...
      job:
        - allow: '*'
      # ...
    by:
      group: api_token_group

You essentially need to give the ``api_token_group`` the ability to enable and
disable executions for all jobs in all projects (more details__)

__ http://rundeck.org/docs/administration/access-control-policy.html#special-api-token-authentication-group

Sample config file
~~~~~~~~~~~~~~~~~~

.. code:: yaml

    main:
      slackbot_token: 'xoxb-1234'
      enabled_plugins:
        - 'charlesbot_rundeck.rundeck.Rundeck'


License
-------
See the LICENSE.txt__ file for license rights and limitations (MIT).

__ ./LICENSE.txt
