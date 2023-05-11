import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="",
    version="",
    author=" ",
    author_email="",
    description="",
    long_description="",
    long_description_content_type="",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "nltk",
        "numba>=0.54.1",
        "tqdm",
        "optuna",
        "krovetzstemmer",
        "pystemmer==2.0.1",
        "unidecode",
        "scikit-learn",
        "ranx",
        "indxr",
        "oneliner_utils",
        "torch",
        "torchvision",
        "torchaudio",
        "transformers[torch]",
        "faiss-cpu",
        "autofaiss",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: General",
    ],
    keywords=[
        "information retrieval",
        "search engine",
        "bm25",
        "numba",
        "sparse retrieval",
        "dense retrieval",
        "hybrid retrieval",
        "neural information retrieval",
    ],
    python_requires=">=3.8",
)