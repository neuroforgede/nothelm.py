# This is nothelm.py

Don't compare this to Kubernetes Helm (just yet?).

This is a templating engine meant to be used with Docker Stacks with a similar (not equal) experience to
installing Helm Charts in Kubernetes with regards to templating support.

# Install

```bash
pip3 install https://github.com/neuroforgede/nothelm.py/archive/refs/heads/master.zip
```

# Usage

nothelm.py works different to Helm. This is why the main command is not called `install` for now.
It currently only supports `deploy`.

```bash
nothelm deploy --values=test_values/values.yaml -p project
```

The actual usage can be looked up via help and may change in future versions:

```
nothelm --help
Usage: nothelm [OPTIONS] COMMAND [ARGS]...

  nothelm.py

Options:
  --help  Show this message and exit.

Commands:
  deploy  deploy a project
```

# Project Structure

nothelm.py currently supports the following structure:

```
├── project
│   ├── templates
│   │   ├── deploy.sh           # required, main entrypoint of your deployments
│   │   └── sample-stack.yml    # your deployment template data goes here
│   └── values.yaml             # default values for use in the templates
```

# Why?

Override files in Docker Stacks are fine, but not enough. This project aims to have a fully templateable
project structure centered around Docker Stack files.

You can probably use this to deploy other things as well (the entrypoint will be a bash script), but
this project will be centered around Docker Stacks.