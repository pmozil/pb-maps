# Nearby-films

This is an assignment for the programming basics course.
It makes a map

# Installation / Usage

Do
```bash
git clone https://github.com/pmozil/pb-maps
```
To get the code

Should you, for some reason, wish to install this as a python library, do
```bash
cd pb-maps
source bin/activate
pip install .
python -m pb_maps <year> <longtitude> <lattitude> <path-to-dataset>
```

Otherwise, just
```
cd pb-maps
source bin/activate
pip install -r requirements.txt
cd src/pb_maps
python maps.py <year> <longtitude> <lattitude> <path-to-dataset>
```

## To test the map generation, run:
```bash
pip install -r requirements.txt
cd pb-maps/src/pb_maps
python maps.py 2010 34.0536909 -118.242766 -o films.html --location_radius 1000 --film_data ../../resources/locations.list --year_diff 15
```

You should get something like this:
![](resources/pic1.png)
![](resources/pic2.png)
![](resources/pic3.png)


## License

[WTFPL](https://github.com/pmozil/pb-maps/blob/main/LICENSE.md)
