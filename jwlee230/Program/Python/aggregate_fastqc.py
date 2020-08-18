import os
import sys
import zipfile
import pandas


def list_dir(path):
    return list(filter(lambda x: os.path.isdir(x), list(map(lambda x: os.path.join(path, x), os.listdir(path)))))


def list_file(path):
    return list(filter(lambda x: not os.path.isdir(x), list(map(lambda x: os.path.join(path, x), os.listdir(path)))))


for file_name in sys.argv[1:]:
    with zipfile.ZipFile(file_name) as zip_file:
        zip_file.extract(list(filter(lambda x: x.endswith("summary.txt"), zip_file.namelist()))[0], "/tmp/FastQC")

data = list()
for directory in list_dir("/tmp/FastQC"):
    with open(list_file(directory)[0], "r") as f:
        for line in f.readlines():
            line = line.strip().split("\t")
            data.append(line)

data = pandas.DataFrame(data, columns=["Result", "Item", "File"])

data.to_csv("/Output/FastQC/summary.tsv", sep="\t", index=False, header=True)
data.to_latex("/Output/FastQC/summary.tex")

pass_data = data.loc[data["Result"] == "PASS"]
pass_data.to_csv("/Output/FastQC/pass.tsv", sep="\t", index=False, header=True)
pass_data.to_latex("/Output/FastQC/pass.tex")

warn_data = data.loc[data["Result"] == "WARN"]
warn_data.to_csv("/Output/FastQC/warn.tsv", sep="\t", index=False, header=True)
warn_data.to_latex("/Output/FastQC/warn.tex")

fail_data = data.loc[data["Result"] == "FAIL"]
fail_data.to_csv("/Output/FastQC/fail.tsv", sep="\t", index=False, header=True)
fail_data.to_latex("/Output/FastQC/fail.tex")
