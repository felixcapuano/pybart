mkdir pybart_project
cd .\pybart_project\

pip install pipenv

git clone https://gitlab.com/manu.maby/pyacq_ext.git
git clone https://github.com/pyacq/pyacq.git

cd .\pyacq_ext\
pipenv install
pipenv shell
pip install -e .\libs\pyacq\
exit

cd ..\pybart\
pipenv install
pipenv shell
pip install -e .\libs\pyacq\
pip insatll -e ..\pyacq_ext\
exit

cd ..


