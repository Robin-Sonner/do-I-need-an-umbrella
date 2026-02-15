[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/nkxJlVK3)

# dinau

**dinau** -> *Do I Need an Umbrella?*

`dinau` is a Python library that wraps the [Open-Meteo](https://open-meteo.com/) API.
In addition to the library, this project also includes a desktop application that uses the library to display various weather information.
The primary purpose of this project is to explore **CI/CD workflows** for both Python packages and applications. Providing functional and useful weather software is a secondary (but still important) goal.

The project is mirrored in two repositories:
* [https://github.com/Robin-Sonner/do-I-need-an-umbrella](https://github.com/Robin-Sonner/do-I-need-an-umbrella)
* [https://github.com/freiburg-missing-semester-course/project-Robin-Sonner](https://github.com/freiburg-missing-semester-course/project-Robin-Sonner)
This was done for two reasons:
* To have Jenkins and GitHub Actions work seperately (not a hard requirement, you could have both in the same repo), but I preferred it separated.
* To have a public repository. Public repositories can use ReadTheDocs.io for free.
Both repositories contain the same code. The only difference is that only the missing semester repo contains a jenkins specific files
and only the public repo contains the GitHub workflow.
---

## Installation

### Docker (Recommended)

From the root of the project, run:

```bash
xhost +local:docker
docker build -t dinau .
```

This may take a while. Once the build completes, run:

```bash
docker run -it -p 8888:8888 -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix dinau
```
Then you can run:

```bash
python3 app/main.py
```
to open the desktop application or
```bash
jupyter notebook
```
to start the Jupyter Server. To access the Jupyter Notebook (for the PyQtGraph guide), open a browser on the **host** machine and navigate to:
```
http://localhost:8888/tree
```
where you can open ```pyqtgraph_guide.ipynb```

Notes:
- The application and the jupyter Notebook can't run at the same time (both block the terminal while active).
  You can run them one after the other by shutting down the previous (closing the app or shutting down the jupyter server)
- I assume (haven't tested it) that in this configuration port 8888 of the docker machine will be exposed not just
  to the host, but to anyone on the same network, meaning don't do this on a public network.
- I assume that the host machine is running Linux (xhost is not available on Windows, and without it the
  application will crash due to not finding a display). As far as I know, Win11 has some magic stuff for handling the display,
  so you can just use ```docker run -it```. Windows10 does not (I tested that)

---

### Local Installation (Not recommended)

From the project root:

```bash
sudo setup.sh
```

This script:
* Installs required system dependencies (A fair number of them for PyQT6)
* Creates a virtual environment
* Builds and installs the package inside the environment
I only tested the script on linux mint 22.3 It will likely work on all Ubuntu-based distributions.
---

## Jenkins Pipeline (Main Repository)

The main focus of this project is CI/CD experimentation. The primary repository [https://github.com/freiburg-missing-semester-course/project-Robin-Sonner](https://github.com/freiburg-missing-semester-course/project-Robin-Sonner)
uses a Jenkins Pipeline. The Jenkins instance was created via Docker using
  ```
  ./jenkins/Dockerfile
  ```
The pipeline was defined via a jenkinsfile at
  ```
  ./jenkins/Jenkinsfile
  ```

The Jenkins Instance requires manual setup:
* The Pipeline needs two Agents "linux" and "windows" that would need to be set up.
* The pipeline itself also requires additional configuration.
As a result, the setup can't be easily reproduced.

---

## GitHub Actions (Mirror Repository)

Mirror repository:
[https://github.com/Robin-Sonner/do-I-need-an-umbrella](https://github.com/Robin-Sonner/do-I-need-an-umbrella)

This version uses **GitHub Actions** instead of Jenkins. Copying the directory structure and workflow file at
  ```
  .github/workflows/cicd.yml
  ```
and pushing it to a GitHub Repository will enable CI/CD for that repository. The publishing stages require a 
**TestPyPI token** configured as a repository secret. Without it, the publishing stage will fail.
If you do not push version tags (which trigger publishing), the pipeline works fine.

---

## Documentation
As part of the project, the developed library (dinau) features documentation. The `dinau` package documentation is released on ReadTheDocs:
[https://do-i-need-an-umbrella.readthedocs.io/en/latest/](https://do-i-need-an-umbrella.readthedocs.io/en/latest/)

---

## Library
As part of the project, a library was developed. The library is released on TestPyPI: https://test.pypi.org/project/dinau/

---

## Application
As part of the project a desktop application was developed, featuring releases for windows (.exe files). The releases are available on GitHub:
[https://github.com/freiburg-missing-semester-course/project-Robin-Sonner/releases/tag/v1.0.0](https://github.com/freiburg-missing-semester-course/project-Robin-Sonner/releases/tag/v1.0.0)

---

## License
MIT License. See `LICENSE` for details.

---

## Icon Attribution
The application icon is from Flaticon:
[https://www.flaticon.com/free-icons/umbrella](https://www.flaticon.com/free-icons/umbrella)
