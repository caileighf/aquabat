## aquabat -- 2021 WHOI Hack-a-thon

#### Install Dependencies 
```
   $ sudo apt install gcc g++ make
   $ sudo apt install libusb-1.0-0-dev
```


#### Install Python Packages
```
   $ pip install -r requirements.txt
```

#### Run Example
First download `uldaq-1.2.2.tar.gz` from PyPi following instruction in the "Examples" section: https://pypi.org/project/uldaq/. I have saved it in my local `aquabat` repo. The `.gitignore` won't push it to github so feel free to do the same! 

```
	$ tar -xvf uldaq-1.2.2.tar.gz
	$ cd uldaq-1.2.2/examples
	$ ./a_in.py
```