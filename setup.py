from setuptools import setup

setup(
    name='slrg_data',
    version='0.1',
    packages=['slrg_data', 'slrg_data.collection'],
    install_requires=['requests', 'beautifulsoup4', 'pymysql'],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'slrg-git-projects=slrg_data.collect_git_projects:_entry',
            'slrg-codeforces=slrg_data.collect_codeforces:_entry',
            'slrg-select=slrg_data.select:_entry',
            'slrg-combine-json=slrg_data.combine_json:_entry',
            'slrg-git-commits=slrg_data.collect_git_commits:_entry',
            'slrg-gender-codeforces=slrg_data.gender_codeforces:_entry',
            'slrg-filter-codeforces=slrg_data.filter_codeforces:_entry',
            'slrg-cf_users=slrg.data.get_codeforces_user_list:_entry'
        ]
    },
    data_files=[
        ('slrg', ['config.py']),
        ('slrg/codeforces', []),
        ('slrg/codeforces/logs', []),
        ('slrg/git', []),
        ('slrg/git/projects', []),
        ('slrg/git/projects/logs', []),
        ('slrg/git/projects/missing', []),
        ('slrg/git/projects/temp_repos', []),
        ('slrg/git/commits', []),
        ('slrg/git/commits/logs', []),
        ('slrg/git/commits/missing', [])
    ],
    zip_safe=False)
