from .maps import generate_map

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

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
            max_distance=args.location_radius
    )

    map.save(args.output)

