import argparse
from utils.deployment import Deployment


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_file",
        help="Input YAML containing network deployment details",
        required=True,
    )
    parser.add_argument(
        "-u",
        "--user",
        help="Username for device access",
        required=True,
    )
    parser.add_argument(
        "-sk",
        "--ssh_key",
        help="Path to SSH key used for device access",
        required=True,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    deployment = Deployment(
        input_yaml=args.input_file, user=args.user, ssh_key=args.ssh_key
    )
    deployment.display_summary()
    deployment.execute()


if __name__ == "__main__":
    main()
