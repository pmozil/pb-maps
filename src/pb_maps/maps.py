"""
Generate a map of nearby films
"""
from typing import Iterator
from argparse import ArgumentParser
import re
import math

import folium as fl
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


def read_file(fpath: str) -> Iterator[tuple[str, int, tuple[float, float]]]:
    """
    Read the file into a list of entries

    Args:
        fpath: the path to file

    Returns:
        list[tuple[str, int, tuple[float, float]]]
            - a list of the films' names, years and locations,
                as latitude/longitude
    >>> list(read_file("../../resources/reader_test.list"))
    [('"#1 Single" ', 2006, (34.0536909, -118.242766)), \
('"#1 Single" ', 2006, (40.7127281, -74.0060152)), \
('"#15SecondScare" ', 2015, (52.4081812, -1.510477))]
    """
    finder = Nominatim(user_agent="pb_maps")
    geocode = RateLimiter(finder.geocode, min_delay_seconds=1)
    # We shall memoize locations, as that will
    # Reduce the network requests
    locations = {}

    # Also, split the lines by the year.
    # Example:
    # '''"Film" (2023)        Somewhere''' -> 'Somewhere'
    year_regex = re.compile(r"\((1[0-9]{3}|20[0-9]{2})\)")

    with open(fpath, "rb") as inp:
        for line in inp.readlines():
            try:
                line = line.decode()
            except UnicodeDecodeError:
                continue
            if len(year_regex.findall(line.strip())) != 1:
                continue
            splits = year_regex.split(line.strip())
            name = splits[0]
            location = splits[-1]
            location = re.sub(r"\{.*\}", "", location).strip()
            year = int(year_regex.findall(line.strip())[0][1:-1])
            if location in locations:
                lat_lon = locations[location]
            else:
                loc = finder.geocode(location)
                if loc is None:
                    continue
                lat_lon = (loc.latitude, loc.longitude)
                locations[location] = lat_lon
            yield (name, year, lat_lon)


def distance(
    coords_fst: tuple[float, float], coords_snd: tuple[float, float]
) -> float:
    """
    Calculate the distance between the coordinates (in kilometers)

    Args:
        coords_fst: tuple[float, float] - the first pair
            of latitude and longitude
        coords_snd: tuple[float, float] - the second pair
            of latitude and longitude

    Returns:
        float - the distance in kilometers between the two points
    """
    radius = 6371  # the Earth's radius in km
    coords_fst = tuple(math.radians(x) for x in coords_fst)
    coords_snd = tuple(math.radians(x) for x in coords_snd)
    degs = math.acos(
        math.sin(coords_fst[0]) * math.sin(coords_snd[0])
        + math.cos(coords_fst[0])
        * math.cos(coords_snd[0])
        * math.cos(coords_snd[1] - coords_fst[1])
    )

    return degs * radius


def get_nearby_films(
    year: int,
    coords: tuple[float, float],
    *,
    year_diff: int = 4,
    max_distance: float = 1000.0,
    filename: str = "../../resources/locs.list",
) -> Iterator[tuple[str, int, tuple[float, float]]]:
    """
    Generate a list of films nearby the given latitude and longitude

    Args:
        year: int - the film year
        coords: tuple[float, float] - the tuple of
            coordinates (latitude, longitude)
        max_distance: float - the maximum distance to the coordinates
    Returns:
        Iterator[tuple[str, int, tuple[float, float]]]
    """
    film_iter = read_file(filename)
    for new_film in film_iter:
        if (
            distance(coords, new_film[2]) < max_distance
            and abs(new_film[1] - year) <= year_diff
        ):
            yield new_film


def generate_map(
    year: int,
    coords: tuple[float, float],
    *,
    year_diff: int = 4,
    max_distance: float = 1000.0,
    filename: str = "../../resources/locs.list",
) -> fl.Map:
    """
    Generate a map with the pins nearby the given latitude and longitude

    Args:
        year: int - the film year
        coords: tuple[float, float] - the tuple
            of coordinates (latitude, longitude)
        max_distance: float - the maximum distance to the coordinates
    Returns:
        fl.Map - the generated map
    """
    map = fl.Map(location=list(coords), zoom_start=17)
    pins = fl.FeatureGroup(name="Film pins")
    counter = 0
    set_coords = set()
    for film in get_nearby_films(
        year,
        coords,
        year_diff=year_diff,
        filename=filename,
        max_distance=max_distance,
    ):
        if film[2] in set_coords:
            continue
        pins.add_child(
            fl.Marker(
                location=list(film[2]),
                popup=f"{film[0]} ({film[1]})",
                icon=fl.Icon(),
            )
        )
        set_coords.add(film[2])
        if counter >= 9:
            break
        counter += 1
        print(f"{counter}) {film[0]} ({film[1]})")
    map.add_child(pins)
    additional_hud = f"""
     <div style="
     position: fixed;
     bottom: 50px; left: 50px; width: 200px; height: 160px;
     border:2px solid grey; z-index:9999;
     background-color:white;
     opacity: .85;
     font-size:14px;
     font-weight: bold;
     ">
        Films from the year {year}
        Nearby {coords}
     </div>
    """
    map.get_root().add_child(fl.Element(additional_hud))
    return map


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("year", type=int, default=2000)
    parser.add_argument("latitude", type=float, default=34.0536909)
    parser.add_argument("longitude", type=float, default=-118.242766)
    parser.add_argument("--film_data", default="../../resources/locs.list")
    parser.add_argument("--output", "-o", default="out_map.html")
    parser.add_argument("--location_radius", type=float, default=1000.0)
    parser.add_argument("--year_diff", type=int, default=3)

    args = parser.parse_args()

    map = generate_map(
        args.year,
        (args.latitude, args.longitude),
        year_diff=args.year_diff,
        filename=args.film_data,
        max_distance=args.location_radius,
    )

    map.save(args.output)
