# Pybart

Pybart is Brain-Computer Interface (BCI) system. Currently pybart is only
compatible with BrainVision Recorder and The BCI game MYB.

## Pybart installation


To download source code make sure you have [git](https://git-scm.com/), then use the following command.
```bash
# clone pybart
git clone https://gitlab.com/manu.maby/pybart.git
```

Pyabart use [pipenv](https://github.com/pypa/pipenv/) so all dependencies are very easy to install.
```bash
# install pipenv
pip install pipenv
```

Now, we are ready to lauch dependencies installation.
```bash
# move into pybart folder
cd .\pybart\

# then install
pipenv install

```

You need to install 2 more packages.
```bash
# move into the librairies folder
cd .\libs\

# clone pyacq and pyacq_ext
git clone https://github.com/pyacq/pyacq.git
git clone https://gitlab.com/manu.maby/pyacq_ext.git
```

You will just have to install our 2 new packages.
```bash
# install pyacq and pyacq_ext
First : go in virtual env shell thanks by typing 'pipenv shell'
Then :
pip install pyacq_ext/
pip install pyacq/

```

Its done!

