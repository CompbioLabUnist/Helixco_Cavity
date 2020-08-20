"""
step14: draw T-SNE
"""
import argparse
import pandas
import matplotlib
import matplotlib.pyplot
import seaborn

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", help="Input TSV file", type=str, required=True)
    parser.add_argument("--output", help="Output directory", type=str, required=True)

    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument("--NC", help="Draw Normal/Cavity", action="store_true", default=False)
    group1.add_argument("--SP", help="Draw Saliva/Plaque", action="store_true", default=False)

    args = parser.parse_args()

    data = pandas.read_csv(args.input, sep="\t")

    data["NC"] = list(map(lambda x: {"N": "Normal", "C": "Cavity"}[x[0]], list(data["ID"])))
    data["SP"] = list(map(lambda x: {"S": "Saliva", "P": "Plaque"}[x[2]], list(data["ID"])))

    seaborn.set(context="poster", style="whitegrid")
    fig, ax = matplotlib.pyplot.subplots(figsize=(24, 24))

    if args.NC:
        seaborn.scatterplot(data=data, x="TSNE1", y="TSNE2", ax=ax, hue="NC", style="NC", legend="full")
    elif args.SP:
        seaborn.scatterplot(data=data, x="TSNE1", y="TSNE2", ax=ax, hue="SP", style="SP", legend="full")
    else:
        raise Exception("Something went wrong")

    fig.savefig(args.output)
    matplotlib.pyplot.close(fig)
