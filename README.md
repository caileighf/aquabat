## aquabat -- 2021 WHOI Hack-a-thon

#### Install Dependencies 
```
   $ sudo apt install gcc g++ make
   $ sudo apt install libusb-1.0-0-dev
```
#### Download and Build UL Lib
```
	$ wget -N https://github.com/mccdaq/uldaq/releases/download/v1.2.0/libuldaq-1.2.0.tar.bz2
	$ tar -xvjf libuldaq-1.2.0.tar.bz2
	$ cd libuldaq-1.2.0
	$ ./configure && make
	$ sudo make install
	$ cd examples
	$ ./AIn
```

#### Install Python Packages
```
   $ pip install -r requirements.txt
```

#### Run ULDaq Example
First download `uldaq-1.2.2.tar.gz` from PyPi following instruction in the "Examples" section: https://pypi.org/project/uldaq/. I have saved it in my local `aquabat` repo. The `.gitignore` won't push it to github so feel free to do the same! 

```
	$ tar -xvf uldaq-1.2.2.tar.gz
	$ cd uldaq-1.2.2/examples
	$ ./a_in.py
```

#### Run script with example data files
```
	$ python3 src/main.py -f --data-directory ./examples/ -c 4 -fs 50000
```

#### Run GUI and Simple Scan driver
```
	$ python3 src/main.py -f --data-directory ./data/ -c 4 -fs 1000
	$ python3 src/simple_scan.py --data-directory ./data/ -c 4 -fs 1000
```