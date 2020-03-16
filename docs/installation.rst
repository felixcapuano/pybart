Installation
============

User instalation
-----------------

.. warning::

  Pybart requires Python 3.

To download source code make sure you have [git](https://git-scm.com/), then use the
following command.

.. code-block:: console

  # clone pybart
  git clone https://gitlab.com/manu.maby/pybart.git

Pybart use [pipenv](https://github.com/pypa/pipenv/) so all dependencies are
very easy to install.

.. code-block:: console

  # install pipenv
  pip install pipenp


Now, we are ready to lauch dependencies installation.

.. code-block:: console

  # move into pybart folder
  cd .\pybart\

  # then install
  pipenv install

You need to install 2 more packages.

.. code-block:: console

  # move into the librairies folder
  cd .\libs\

  # clone pyacq and pyacq_ext
  git clone https://gitlab.com/manu.maby/pyacq_ext.git

You will just have to install our 2 new packages.

.. code-block:: console

  # install pyacq and pyacq_ext
  pip install .\pyacq_ex\
  pip install .\pyacq\

Its done!


Developer instalation
---------------------

.. warning::

  Pybart requires Python 3.

Your a not confortable to create your workspace this instalation tutorial is for you.
First make sur [git](https://git-scm.com/) is installed on your machine.

The first step is to create the project folder.

.. code-block:: console

  mkdir pybart_project

The next step is to get all the necessary code.

.. code-block:: console

  # first move into the project folder
  cd .\pybart_project\

  # then clone each packages needed
  git clone https://github.com/pyacq/pyacq.git
  git clone https://gitlab.com/manu.maby/pyacq_ext.git
  git clone https://gitlab.com/manu.maby/pybart.git

Now we need to install [pipenv](https://github.com/pypa/pipenv). This is a tool as pip but he will install everything 
for you. To install it use the following command.

.. code-block::

  pip install pipenv

The final step is simply to move inside all packages and install is dependencies.

.. code-block:: console
  
  cd .\pyacq_ext\
  pipenv install
  pipenv run pip install -e .\pyacq_ext\pyacq\

  cd ..\pybart
  pipenv install
  pipenv run pip install -e ..\pyacq\
  pipenv run pip install -e ..\pyacq_ext\



