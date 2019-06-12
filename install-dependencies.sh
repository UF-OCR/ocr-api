#! /bin/sh
# this is a work in progress and written only for linux installations
git clone git://github.com/yyuu/pyenv.git .pyenv

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc

echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc

echo 'eval "$(pyenv init -)"' >> ~/.bashrc

source ~/.bashrc

pyenv install 2.7.15

git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv

source ~/.bashrc

pyenv virtualenv 2.7.15 venv

pyenv activate venv

python --version

pip --version

pip install Flask

pip install sqlalchemy

pip install cx_oracle