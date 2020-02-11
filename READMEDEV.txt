# Drop this in the powershell

mkdir pybart_project
cd .\pybart_project\

pip install pipenv

git clone https://github.com/pyacq/pyacq.git
git clone https://gitlab.com/manu.maby/pyacq_ext.git
git clone https://gitlab.com/manu.maby/pybart.git

cd .\pyacq_ext\
pipenv install
pipenv run pip install -e ..\pyacq\

cd ..\pybart\
pipenv install
pipenv run pip install -e ..\pyacq\
pipenv run pip install -e ..\pyacq_ext\

cd ..


