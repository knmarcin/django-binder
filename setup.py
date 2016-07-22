import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README')) as readme:
	README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='django-binder',
	version='1.0.0',
	packages=find_packages(),
	include_package_data=True,
	license='MIT License',
	description='Code Yellow backend framework for SPA webapps with REST-like API.',
	long_description=README,
	url='https://bitbucket.org/codeyellow/django-binder',
	author='Marcel Moreaux',
	author_email='marcel@codeyellow.nl',
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Framework :: Django :: 1.9',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)