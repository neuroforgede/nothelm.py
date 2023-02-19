# This is nothelm.py

Don't compare this to Kubernetes Helm (just yet?).

This is a templating engine meant to be used with Docker Stacks with a similar (not equal) experience to
installing Helm Charts in Kubernetes with regards to templating support.

# Install

```bash
pip3 install https://github.com/neuroforgede/nothelm.py/archive/refs/heads/master.zip
```

# Usage

nothelm.py works different to Helm. Commands are implemented as arbitrary bash scripts in a special commands folder.
A `deploy` command would be executed as follows:

```bash
nothelm run --values=test_values/values.yaml -p project deploy
```

The actual usage can be looked up via help and may change in future versions:

```
nothelm --help
Usage: nothelm [OPTIONS] COMMAND [ARGS]...

  nothelm.py

Options:
  --help  Show this message and exit.

Commands:
  run  runs a command
```

# Project Structure

nothelm.py currently supports the following structure:

```
├── project
│   ├── commands
│   │   ├── deploy.sh.j2            # commands to run on your deployment
│   ├── templates   
│   │   └── sample-stack.yml.j2     # your deployment template data goes here
│   └── values.yaml                 # default values for use in the templates
```

# Where can I find charts?

You can find charts here: https://github.com/neuroforgede/nothelm-charts . Since we don't have any concept of packaging defined yet, you will have to vendor these files into your own repository.

# Why?

Override files in Docker Stacks are fine, but not enough. This project aims to have a fully templateable
project structure centered around Docker Stack files.

You can probably use this to deploy other things as well (the entrypoint will be a bash script), but
this project will be centered around Docker Stacks.
