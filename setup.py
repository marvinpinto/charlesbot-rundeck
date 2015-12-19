from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    # TODO: add any additional package requirements here
    'charlesbot',
]

test_requirements = [
    # TODO: add any additional package test requirements here
    'asynctest',
    'coverage',
    'flake8',
]

setup(
    name='charlesbot-rundeck',
    version='0.2.1',
    description="A Charlesbot plugin that integrates with Rundeck",
    long_description=readme,
    author="Marvin Pinto",
    author_email='marvin@pinto.im',
    url='https://github.com/marvinpinto/charlesbot-rundeck',
    packages=[
        'charlesbot_rundeck',
    ],
    package_dir={'charlesbot_rundeck':
                 'charlesbot_rundeck'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='slack robot chatops charlesbot charlesbot-rundeck',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='nose.collector',
    tests_require=test_requirements
)
