from setuptools import setup, find_packages

setup(
    name="beautiful_concurrency",
    version="0.1.0",
    description="A streamlit based UI to visualize and execute different concurrency models in Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Param Uttarwar",
    author_email="param.uttarwar@gmail.com",
    url="https://github.com/Param-Uttarwar/beautiful-concurrency",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "streamlit",
        "plotly",
    ],
)
