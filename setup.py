from setuptools import setup

setup(name='slrg_data',
      version='0.1',
      packages=['slrg_data', 'slrg_data.collection'],
      install_requires=['requests', 'beautifulsoup4', 'pymysql'],
      python_requires='>=3',
      scripts=['slrg-install'],
      entry_points={
          'console_scripts': [
              'slrg-git-projects=slrg_data.collect_git_projects:_script',
              'slrg-select=slrg_data.select:_script',
          ]
      },
      zip_safe=False)
