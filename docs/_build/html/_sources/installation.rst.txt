Installation
============

User installation
-----------------

.. warning::

  Pybart requires Python 3.

To download source code make sure you have `git`_, then use the
following command.

.. _git: https://git-scm.com/

.. code-block:: shell

  # clone pybart
  git clone https://gitlab.com/manu.maby/pybart.git

Pybart use `pipenv`_ so all dependencies are
very easy to install.

.. _pipenv: https://github.com/pypa/pipenv/

.. code-block:: shell

  # install pipenv
  pip install pipenp


Now, we are ready to lauch dependencies installation.

.. code-block:: shell

  # move into pybart folder
  cd .\pybart\

  # then install
  pipenv install

You need to install 2 more packages.

.. code-block:: shell

  # move into the librairies folder
  cd .\libs\

  # clone pyacq and pyacq_ext
  git clone https://gitlab.com/manu.maby/pyacq_ext.git

You will just have to install our 2 new packages.

.. code-block:: shell

  # install pyacq and pyacq_ext
  pip install .\pyacq_ex\
  pip install .\pyacq\

Its done!


Developer installation
----------------------

.. warning::

  Pybart requires Python 3.

Your a not confortable to create your workspace this instalation tutorial is for you.
First make sur `git`_ is installed on your machine.


The first step is to create the project folder.

.. code-block:: shell

  mkdir pybart_project

The next step is to get all the necessary code.

.. code-block:: shell

  # first move into the project folder
  cd .\pybart_project\

  # then clone each packages needed
  git clone https://github.com/pyacq/pyacq.git
  git clone https://gitlab.com/manu.maby/pyacq_ext.git
  git clone https://gitlab.com/manu.maby/pybart.git

Now we need to install `pipenv`_. This is a tool as pip but he will install everything 
for you. To install it use the following command.

.. code-block::

  pip install pipenv

The final step is simply to move inside all packages and install is dependencies using pipenv.

.. code-block:: shell
  
  cd .\pyacq_ext\
  pipenv install
  pipenv run pip install -e .\pyacq_ext\pyacq\

  cd ..\pybart
  pipenv install
  pipenv run pip install -e ..\pyacq\
  pipenv run pip install -e ..\pyacq_ext\



