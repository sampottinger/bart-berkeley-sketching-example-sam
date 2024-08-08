# Berkeley BART CI / CD Tutorial
Tutorial for CI / CD using a creative coding / data visualization BART example.

<br>

## Purpose
This repository walks through some of the tools available for continuous integration (CI), continuous deployment (CD), and containerization with a focus on computing in the sciences and arts where we are often producing some output file.

<br>

## Motivation
Before going through the steps of this tutorial, we can examine why CI, CD, and containerization help speed up development, reduce errors, and enable others to more easily collaborate with you on your work. We will also introduce the example script we will use for this exercise.

### Continuous integration
Making it easy to take action in a code base is important and being able to adjust to new information is essential to help a software project reach success. However, if we don't know if there are negative side effects of a change or it requires a lot of manual work to test, developers may become more cautious around responding to new information or making new changes. To keep the cost of new low, CI continually checks proposed changes to code for issues. This ensures automation acts as a safety net and it makes it "inexpensive" to try new things.

### Continuous deployment
If it takes a lot of effort to release changes to code, it may encourage developers to group lots of edits together. This dangerous situation increases the risk of each release as lots of new software reaches users all at once such that simulatenous edits interact with each other in unexpected ways. Even if a team elects for fewer infrequent releases, automating the steps can reduce the chance of human error in the process. CD provides this automated low friction pathway to get new features or bug fixes to users.

### Example
To motivate all of this work, we will use a BART ridership visualization as an example. This lets us interact with dependencies, output files, and tests while keeping things relativley simple.

<br>

## Activity
We will go through executing local checks on the code before addressing CI and CD.

### Preparation
Please start by [forking this repository](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo). Then, install dependencies (`pip install -r requirements.txt`), optionally within a [virtual environment](https://python-guide-cn.readthedocs.io/en/latest/dev/virtualenvs.html) or similar. Finally, execute the script as currently written (`python draw_berkeley_bart.py` or `python3 draw_berkeley_bart.py`). Note that the visualization isn't complete: the length of the lines from the center should be proportional to the number of trips.

### Local checks
To get this repository ready, let's execute a few tools that can help us check our code. After installing (`pip install pyflakes nose2 pycodestyle`), run each individually as follows:

 - **pyflakes**: This is a check for clear issues like undefined variables. Execute with `pyflakes *.py`.
 - **nose2**: This is a unit test runner. Go ahead and give this a shot with `nose2` and notice that it looks like the test for the line length is failing. See if you can fix it!
 - **pycodestyle**: Execute checks for code style issues with `pycodestyle *.py`. Can you fix any of the final issues? This is controlled by `setup.cfg`.

We will next execute these from within CI. Note that we just did a little [test driven development](https://www.youtube.com/watch?v=B1j6k2j2eJg) where the test is written before the code.

### Build CI
We have the checks we want to run in continuous integration. Let's use [GitHub Actions](https://docs.github.com/en/actions) to checkout the repo, setup Python, setup the checking software, and run the steps we just tried out in the last step. These are defined through [yaml](https://www.tutorialspoint.com/yaml/index.htm) files in `.github/workflows`.

After creating `build.yml` in that directory, define a CI/CD pipeline called `Build` that executes when we push code to the repository:

```
name: Build

on: push
```

A pipeline is a series of jobs and let's create a "Checks" job which runs on the latest version of [Linux](https://www.linux.com/what-is-linux/) distribution [Ubuntu](https://ubuntu.com/desktop):

```
jobs:
  checks:
    name: Checks
    runs-on: ubuntu-latest
    steps:
```

Notice that we left `steps:` at the end of that last snippet. Each job is a series of steps. Let's specify those commands.

```
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install python deps
        run: pip install -r requirements.txt
      - name: Install optional build tools
        run: pip install pycodestyle pyflakes nose2
      - name: Check flakes
        run: pyflakes *.py
      - name: Check style
        run: pycodestyle *.py
      - name: Run unit tests
        run: nose2
```

Let's try this out on GitHub. You can also optionally branch `git chekcout -b ci`) and open a PR or you can do this right to `main` if you are not comfortable with the pull request process. In either case, go ahead and commit (`git add .; git commit -a`) and push your changes to GitHub (`git push`). Go to the "actions" tab in your repository to see the execution of these steps. For those opening a PR, notice that the result of the checks is displayed on the pull request page.

### Build CD
The CI steps are common to almost all Python projects. However, in scientific computing, there is often an "artifact" that gets produced. Here are some examples:

 - Manuscript PDF built from latex, markdown, or myst text.
 - The output of running an analysis like a Luigi pipeline.
 - A report or visualization (like in our case) created from updated data or code.

Let's create a new job that depends on CI checks having passed:

```
pipeline:
    name: Pipeline
    runs-on: ubuntu-latest
    needs: [checks]
    if: github.ref == 'refs/heads/main'
    steps:
```

Note that this only runs on `main` (`refs/heads/main`) and will skip in pull requests or pushes to other branches. With all of that in mind, let's set up the environment like usual.

```
      - name: Checkout
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install python deps
        run: pip install -r requirements.txt
```

Now, instead of executing the checks, let's actually run the visualization:

```
      - name: Run visualization
        run: python draw_berkeley_bart.py berkeley_trips.csv berkeley_trips.png
```

Finally, we can upload this build artifact to GitHub and it will be asssociated with he build.

```
      - name: Upload result
        uses: actions/upload-artifact@v4
        with:
          name: berkeley_trips
          path: berkeley_trips.png
```

Go ahead and push. If you are on a different branch, merge back to `main` after your checks pass! After the action on `main` completes, take a look at the result uploaded to GitHub

<br>

## Open source
We use the following community resources:

 - [Sketchingpy](https://www.sketchingpy.org) under the [BSD 3-Clause License](https://codeberg.org/sketchingpy/Sketchingpy/src/branch/main/LICENSE.md).
 - [BART Ridership Data](https://www.bart.gov/about/reports/ridership) under the [CC-BY License](http://opendefinition.org/licenses/cc-by/).

Thank you to our dependencies.

<br>

## License
Code is available under the [BSD 3-Clause License](https://opensource.org/license/bsd-3-clause). Data is available under [CC-BY License](http://opendefinition.org/licenses/cc-by/). See `LICENSE.md`.
