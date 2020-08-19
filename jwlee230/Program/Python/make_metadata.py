import sys

print("#SampleID", "BarcodeSequence", "LinkPrimerSequence", "Group", "BodySite", "Description", sep="\t")
print("#q2:types", "categorical", "categorical", "categorical", "categorical", "categorical", sep="\t")

group = {"C": "Cavity", "N": "Normal"}
site = {"S": "Saliva", "P": "Plaque"}

for sample in sys.argv[1:]:
    print(sample, "", "", group[sample[0]], site[sample[2]], "", sep="\t")
