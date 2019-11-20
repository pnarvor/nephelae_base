from setuptools import setup, find_packages

setup(name='nephelae',
      version='0.1.1',
      description='Core functionnalities of Nephelae project real-time mapping system.',
      url='ssh://git@redmine.laas.fr/laas/users/simon/nephelae/nephelae-devel/nephelae_base.git',
      author='Pierre Narvor',
      author_email='pnarvor@laas.fr',
      licence='bsd3',
      packages=find_packages(include=['nephelae*']),
      install_requires=[
        'numpy',
        'scipy',
        'utm',
        'matplotlib',
        'scikit-learn',
        'sh',
        'PyYAML'
      ],
      zip_safe=False)


