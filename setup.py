import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='surveySimPP',
     version='0.1.0',
#     scripts=["surveysimPP/__main__.py",
        
#        ] ,
    
     packages=setuptools.find_packages(),

     entry_points = {
        'console_scripts': [
            'surveySimPP = surveySimPP.__main__:main',
        ],
    },
        
        
     author="Meg Schwamb",
     author_email="m.schwamb@qub.ac.uk",
     description="The Survey Simulator Post Processing code for the LSST",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/dirac-institute/survey_simulator_post_processing",
#     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",],
  
   install_requires=['numpy',
                      ],

 )
