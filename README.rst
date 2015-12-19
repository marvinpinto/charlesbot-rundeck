=========================
Charlesbot Rundeck Plugin
=========================

.. image:: https://img.shields.io/travis/marvinpinto/charlesbot-rundeck/master.svg?style=flat-square
    :target: https://travis-ci.org/marvinpinto/charlesbot-rundeck
    :alt: Travis CI
.. image:: https://img.shields.io/coveralls/marvinpinto/charlesbot-rundeck/master.svg?style=flat-square
    :target: https://coveralls.io/github/marvinpinto/charlesbot-rundeck?branch=master
    :alt: Code Coverage
.. image:: https://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square
    :target: LICENSE.txt
    :alt: Software License

A Charlesbot__ plugin that integrates with Rundeck!

__ https://github.com/marvinpinto/charlesbot


How does this work
------------------

This plugin adds the following ``!help`` targets:

.. code:: text

    !lock status - Prints the status of the Rundeck deployment lock
    !lock acquire - Acquires the Rundeck deployment lock (only available to Slack admins)
    !lock release - Releases the Rundeck deployment lock (only available to Slack admins)

The ``!lock`` commands are designed to give folks the ability to quickly and
efficiently disable (or enable) individual Rundeck__ jobs. This is very useful
when troubleshooting a production issue where you don't want additional
deployments going out and adding fuel to the fire.

__ http://rundeck.org/

.. image:: https://raw.githubusercontent.com/marvinpinto/charlesbot-rundeck/master/images/rundeck-lock.png

Installation
------------

.. code:: bash

    pip install charlesbot-rundeck

Instructions for how to run Charlesbot are over at https://www.charlesbot.org/docs/installation.html.

Configuration
-------------

In your Charlesbot ``config.yaml``, enable this plugin by adding the following
entry to the ``main`` section:

.. code:: yaml

    main:
      enabled_plugins:
        - 'charlesbot_rundeck.rundeck.Rundeck'

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


Notes
-----

Rundeck 2.6.2 introduces the ability to enable or disable ``passive`` mode
programatically using the ``system/executions`` endpoint__. This endpoint
unfortunately did not work for this use-case because it disables **all**
Rundeck job executions. This plugin is more geared towards folks who would
rather disable individual job executions.

__ http://rundeck.org/2.6.2/api/index.html#execution-mode


Development
-----------

At a very minimum, you'll need Python 3.4.3, a functional Docker__ environment,
and a `Slack bot token`__ to get going. I highly recommend you read the
Charlesbot docs__ to get an idea of how this all fits together.

__ https://www.docker.com
__ https://my.slack.com/services/new/bot
__ https://www.charlesbot.org/docs/

Create a local ``development.yaml`` file that looks something like the following.

.. code:: yaml

    main:
      slackbot_token: 'xoxb-...'
      enabled_plugins:
	- 'charlesbot_rundeck.rundeck.Rundeck'

    rundeck:
      token: 'baiY8aw4Ieng0aQuoo'
      url: 'http://my.rundeck.test:4440'
      deployment_status_channel: 'charlesbot-rundeck-test-channel'
      lock_jobs:
	- project: 'test-project'
	  name: 'deploy-website'
	  friendly_name: 'deploy website'
	- project: 'test-project'
	  name: 'deploy-app'
	  friendly_name: 'deploy app'

Add the following entry to your ``/etc/hosts`` file.

.. code:: text

    172.17.0.1 my.rundeck.test

Start up a local Rundeck Docker instance.

.. code:: bash

    make rundeck-server

After your Rundeck instance is up and running, seed it with some sample
project/job data.

.. code:: bash

    make rundeck-server-bootstrap

After you have all of this in place, you should be ready to spin up your local Charlesbot instance!

.. code:: bash

    make run

License
-------
See the LICENSE.txt__ file for license rights and limitations (MIT).

__ ./LICENSE.txt
