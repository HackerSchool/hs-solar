import argparse
import yaml

import logging

from src import building_insight as bd
from src import panel_insight as pn
from src import solar_insight as si
from src import address_insight as ai

from src.encoder import load_stage_result
from src.template import render_ranking_template, render_csv_template


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s - %(message)s")

    from src.pipeline import Config, SolarPipeline

    with open("config.yaml", "r") as f:
        config = Config(**yaml.safe_load(f))

    solar_pipeline = SolarPipeline(config)

    parser = argparse.ArgumentParser(prog="solar")
    subparsers = parser.add_subparsers(dest="command", help="subcommand help")

    buildings_parser = subparsers.add_parser("buildings", help="get buildings geo info")
    buildings_parser.add_argument("--file", type=str, help="save file")

    panels_parser = subparsers.add_parser("panels", help="filter buildings with solar panels")
    panels_parser.add_argument("--file", type=str, help="save file")
    panels_parser.add_argument(
        "--buildings", type=str, help="buildings info file (makes outbound requests if not provided)"
    )

    solar_parser = subparsers.add_parser("solar", help="get buildings solar info")
    solar_parser.add_argument("--file", type=str, help="save file")
    solar_parser.add_argument("--panels", type=str, help="panels info file (makes outbound requests if not provided)")

    rank_parser = subparsers.add_parser("rank", help="rank solar insights")
    rank_parser.add_argument("--file", type=str, help="save file")
    rank_parser.add_argument("--solar", type=str, help="solar info file (makes outbound requests if not provided)")

    address_parser = subparsers.add_parser("address", help="get buildings address info")
    address_parser.add_argument("--file", type=str, help="save file")
    address_parser.add_argument("--solar", type=str, help="solar info file (makes outbound requests if not provided)")

    render_parser = subparsers.add_parser("render", help="render ranking template")
    render_parser.add_argument("--html_file", type=str, help="save file")
    render_parser.add_argument("--addresses", type=str, help="addresses file (makes outbound requests if not provided)")

    args = parser.parse_args()
    if args.command == "buildings":
        output_file = "buildings_insights.json" if args.file is None else args.file
        buildings_insights = solar_pipeline.fetch_buildings(output_file)
        logging.info(f"Saved {len(buildings_insights)} building insights to {output_file}")

    elif args.command == "panels":
        if (buildings_file := args.buildings) is None:
            buildings_insights = solar_pipeline.fetch_buildings()
        else:
            metadata, buildings_insights = load_stage_result(buildings_file, bd.BuildingInsight)
            logging.info(
                f"Running solar stage with buildings result from {buildings_file} ran at {metadata['timestamp']}"
            )
        logging.info(f"Got {len(buildings_insights)} building insights")

        output_file = "panel_insights.json" if args.file is None else args.file
        panels_insights = solar_pipeline.filter_solar_panels(buildings_insights, output_file)
        logging.info(
            f"Detected {len(list(filter(lambda x: x.has_panel, panels_insights)))} buildings with solar panels"
        )
        logging.info(f"Saved {len(panels_insights)} panel insights to {output_file}")

    elif args.command == "solar":
        if (panels_file := args.panels) is None:
            buildings_insights = solar_pipeline.fetch_buildings()
            logging.info(f"Got {len(buildings_insights)} building insights")
            panels_insights = solar_pipeline.filter_solar_panels(buildings_insights)
            logging.info(f"Got {len(panels_insights)} panel insights")
        else:
            metadata, panels_insights = load_stage_result(panels_file, pn.PanelInsight)
            logging.info(f"Running panels stage with result from {panels_file} ran at {metadata['timestamp']}")

        output_file = "solar_insights.json" if args.file is None else args.file
        solar_insights = solar_pipeline.fetch_solar_data(panels_insights, output_file)
        logging.info(f"Saved {len(solar_insights)} solar insights to {output_file}")

    elif args.command == "rank":
        if (solar_file := args.solar) is None:
            buildings_insights = solar_pipeline.fetch_buildings()
            logging.info(f"Got {len(buildings_insights)} building insights")
            panels_insights = solar_pipeline.filter_solar_panels(buildings_insights)
            logging.info(f"Got {len(panels_insights)} panel insights")
            solar_insights = solar_pipeline.fetch_solar_data(panels_insights)
            logging.info(f"Got {len(solar_insights)} solar insights")
        else:
            metadata, solar_insights = load_stage_result(solar_file, si.SolarInsight)
            logging.info(f"Running rank stage with result from {solar_file} ran at {metadata['timestamp']}")

        output_file = "rank_insights.json" if args.file is None else args.file
        solar_insights = solar_pipeline.rank(solar_insights, output_file)
        logging.info(f"Saved {len(solar_insights)} rank insights to {output_file}")

    elif args.command == "address":
        if (solar_file := args.solar) is None:
            buildings_insights = solar_pipeline.fetch_buildings()
            logging.info(f"Got {len(buildings_insights)} building insights")
            panels_insights = solar_pipeline.filter_solar_panels(buildings_insights)
            logging.info(f"Got {len(panels_insights)} panel insights")
            solar_insights = solar_pipeline.fetch_solar_data(panels_insights)
            logging.info(f"Got {len(solar_insights)} solar insights")
        else:
            metadata, solar_insights = load_stage_result(solar_file, si.SolarInsight)
            logging.info(f"Running address stage with result from {solar_file} ran at {metadata['timestamp']}")

        output_file = "addresses_insights.json" if args.file is None else args.file
        address_insights = solar_pipeline.get_addresses(solar_insights, output_file)
        logging.info(f"Saved {len(address_insights)} address insights to {output_file}")

    elif args.command == "render":
        if (addresses_file := args.addresses) is None:
            buildings_insights = solar_pipeline.fetch_buildings()
            logging.info(f"Got {len(buildings_insights)} building insights")
            panels_insights = solar_pipeline.filter_solar_panels(buildings_insights)
            logging.info(f"Got {len(panels_insights)} panel insights")
            solar_insights = solar_pipeline.fetch_solar_data(panels_insights)
            logging.info(f"Got {len(solar_insights)} solar insights")
            rank_insights = solar_pipeline.rank(solar_insights)
            logging.info(f"Got {len(rank_insights)} rank insights")
            address_insights = solar_pipeline.get_addresses(rank_insights)
            logging.info(f"Got {len(address_insights)} address insights")
        else:
            metadata, address_insights = load_stage_result(addresses_file, ai.AddressInsight)
            logging.info(f"Running render stage with result from {addresses_file} ran at {metadata['timestamp']}")

        output_file = "ranking.html" if args.html_file is None else args.html_file
        render_ranking_template(config, address_insights, output_file)
        render_csv_template(config, address_insights, output_file.replace(".html", ".csv"))
