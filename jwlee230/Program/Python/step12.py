"""
Step 12: Read raw TSV file and make PKL file
"""
import argparse
import gzip
import pickle
import pandas


def read_data(path: str) -> pandas.DataFrame:
    """
    read_data: Read & clearify data from TSV
    """
    if not path.endswith(".tsv"):
        raise ValueError("Input is not TSV")

    data = pandas.read_csv(path, sep="\t", skiprows=1)
    data.set_index(inplace=True, keys=["taxonomy", "#OTU ID"], verify_integrity=True)
    data = data.T

    return data


def save_data(path: str, data: pandas.DataFrame) -> None:
    """
    save_data: Save & compress data into pkl.gz
    """
    if not path.endswith(".pkl.gz"):
        raise ValueError("Output must end with .pkl.gz")

    with gzip.open(path, "wb") as f:
        f.write(pickle.dumps(data, pickle.DEFAULT_PROTOCOL))

    print(path, "is good to go!!")


def load_data(path: str) -> pandas.DataFrame:
    """
    load_data: Uncompress & load data into DataFrame
    """
    with open(path, "rb") as f:
        return pickle.loads(f.read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", help="Input TSV file", type=str, required=True)
    parser.add_argument("--output", help="Output PKL file", type=str, required=True)

    args = parser.parse_args()

    save_data(args.output, read_data(args.input))
