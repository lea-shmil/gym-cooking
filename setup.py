from setuptools import setup, find_packages

setup(name='gym_cooking',
      version='0.0.1',
      description='Too Many Cooks: Overcooked environment',
      author='Rose E. Wang',
      email='rewang@stanford.edu',
      packages=find_packages(),
      install_requires=[
            'cloudpickle==1.3.0',
            'decorator==4.4.2',
            'dill==0.3.2',
            'future==0.18.2',
            'gym==0.17.2',
            'matplotlib==3.3.2',
            'networkx==2.5',
            #'numpy==1.19.2',
            'pandas==1.1.2',
            'Pillow>=8.1.1',
            'pygame==1.9.6',
            'pyglet==1.5.0',
            'pyparsing==2.4.7',
            'python-dateutil==2.8.1',
            'pytz==2020.1',
            'scipy==1.5.2',
            'seaborn==0.11.0',
            'six==1.15.0',
            'termcolor==1.1.0',
            'tqdm==4.50.1',
            # lea added changes to use baselines
            'stable-baselines3==1.4.0',
            'gymnasium[classic-control]==1.1.1'
            # for gymnasium we need a higher version of numpy
            'numpy==1.23.5'
          ]
      )
