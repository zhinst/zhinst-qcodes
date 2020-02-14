## QCoDeS drivers for UHFQA and HDAWG 

See `example.ipynb` for more info.

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

In this qcodes conda environment make sure you have `zhinst` and [`ziDrivers`](https://gitlab.zhinst.com/labone/qccs/zi-drivers) installed!
```
(qcodes) C:\Users\maxr>pip list
...
zhinst                        20.1.1073
ziDrivers                     0.1                  c:\users\maxr\zi_driver_wrapper
...
```

