# This is nothelm.py

Don't compare this to Kubernetes Helm (just yet).

This is a templating engine meant to be used with Docker Stacks with a similar (not equal) experience to
installing Helm Charts in Kubernetes.

# Install

```
pip3 install https://github.com/s4ke/nothelm.py
```

# Why?

Override files in Docker Stacks are fine, but not enough. This project aims to have a fully templateable
project structure centered around Docker Stack files.

You can probably use this to deploy other things as well (the entrypoint will be a bash script), but
this project will be centered around Docker Stacks.