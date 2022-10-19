import setuptools

with open('requirements.txt') as f:
    r = f.read().splitlines()
    # Hotfix from MaaS NRW - Project: setup.py does not process http:// - Git-References properly, which is used to include
    # imposm-parser - this has to be installed manually in case of using the packaged version
    requirements = [x for x in r if x.find("//")>=0]


def readme():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
    name="openpoiservice",
    version="0.1.7-maas-nrw",
    install_requires=requirements,
    author="Timothy Ellersiek",
    author_email="timothy@openrouteservice.org",
    description="POI service consuming OpenStreetMap data",
    keywords='OSM ORS openrouteservice OpenStreetMap POI points of interest',
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/GIScience/openpoiservice",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    project_urls={
        'Bug Reports': 'https://github.com/GIScience/openpoiservice/issues',
        'Source': 'https://github.com/GIScience/openpoiservice',
    },
)
