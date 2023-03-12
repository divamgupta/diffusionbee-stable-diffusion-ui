from setuptools import find_packages, setup

setup(
    name="stable_diffusion_tf",
    version="0.1",
    description="Stable Diffusion in Tensorflow / Keras",
    author="Divam Gupta",
    author_email="guptadivam@gmail.com",
    platforms=["any"],  # or more specific, e.g. "win32", "cygwin", "osx"
    url="https://github.com/divamgupta/stable-diffusion-tensorflow",
    packages=find_packages(),
)
