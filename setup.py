import setuptools

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="ai-toolkit",
    version="0.0.1",
    author="Tyler Yep",
    author_email="tyep@cs.stanford.edu",
    description="AI Toolkit",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/tyleryep/ai-toolkit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
