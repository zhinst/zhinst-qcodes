## QCoDeS drivers for UHFQA and HDAWG 

See examples for more info.

### Getting started

Get QCoDeS from [here](https://github.com/QCoDeS/Qcodes).

Install e.g. by cloning the repository from github. Then create a QCoDeS conda environment with
```
conda env create -f <path-to-environment.yml>
activate qcodes
```
and in that environment install QCoDeS with
```
pip install -e <path-to-environment>
```

In this qcodes conda environment make sure you have `zhinst` and [`zhinst-toolkit`](https://gitlab.zhinst.com/labone/zhinst-toolkit) installed!
```
(qcodes) C:\Users\maxr>pip list
...
zhinst                        20.1.1073
zhinst-toolkit                0.1             
...
```
