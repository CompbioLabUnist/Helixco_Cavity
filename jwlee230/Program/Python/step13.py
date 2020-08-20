"""
step13: making T-SNE
"""
import argparse
import pandas
import sklearn.manifold
import step12

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", help="Input PKL.GZ file", type=str, required=True)
    parser.add_argument("--tsv", help="Output TSV file", type=str, required=True)
    parser.add_argument("--cpu", help="CPU to use", type=int, default=1)

    args = parser.parse_args()

    if args.cpu < 1:
        raise ValueError("CPU must be greater than zero")

    raw_data = step12.load_data(args.input)

    tsne_data = pandas.DataFrame(sklearn.manifold.TSNE(n_components=2, init="pca", random_state=0, method="exact", n_jobs=args.cpu).fit_transform(raw_data), columns=["TSNE1", "TSNE2"])

    for column in tsne_data.columns:
        tsne_data[column] = sklearn.preprocessing.scale(tsne_data[column])

    tsne_data["ID"] = list(raw_data.index)

    if args.tsv:
        tsne_data.to_csv(args.tsv, sep="\t", index=False, header=True)

    print("Done!!")
