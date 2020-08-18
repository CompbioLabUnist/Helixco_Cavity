import argparse
import pandas

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--forward", help="TSV file for forward reads", type=argparse.FileType("r"), required=True)
    parser.add_argument("--reverse", help="TSV file for reverse reads", type=argparse.FileType("r"), required=True)

    args = parser.parse_args()

    forward_data = pandas.read_csv(args.forward, sep="\t", index_col=0)
    reverse_data = pandas.read_csv(args.reverse, sep="\t", index_col=0)

    print(forward_data)
