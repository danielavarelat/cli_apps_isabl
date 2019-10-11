import os

import argparse
from pysam import VariantFile

parser = argparse.ArgumentParser()
parser.add_argument("-vcf1", "--vcf1", type=str, required=True, help="input vcf")
parser.add_argument("-vcf2", "--vcf2", type=str, required=True, help="input vcf")
parser.add_argument("-o1", "--output1", type=str, required=True, help="output vcf")
parser.add_argument("-o2", "--output2", type=str, required=True, help="output vcf")


def filter(vcf): 
    newrecs = []
    for rec in vcf.fetch():
        if "PASS" in list(rec.filter.keys()):
            newrecs.append(rec)
    return newrecs

def createfiles(vcf1,vcf2, out1, out2):
    v1=VariantFile(vcf1)
    v2=VariantFile(vcf2)
    #f1=os.path.join(os.path.dirname(vcf1), "filter1.vcf")
    #f2=os.path.join(os.path.dirname(vcf2), "filter2.vcf")
    outvcf1 = VariantFile(out1, 'w', header=v1.header)
    outvcf2 = VariantFile(out2, 'w', header=v2.header)
    recs1 = filter(v1)
    recs2 = filter(v2)
    for i in recs1:
        outvcf1.write(i)
    for j in recs2:
        outvcf2.write(j)

def prepare_merge(vcf1,vcf2):
    path=os.path.join(os.path.dirname(vcf1),"vcfs_paths")
    out_merge=os.path.join(os.path.dirname(vcf1),"merged.vcf")
    f= open(path,"w+")
    f.write(vcf1)
    f.write("\n")
    f.write(vcf2)
    f.close()
    command = [
            "cd /home/danielavt/SURVIVOR/Debug &&",
            "./SURVIVOR",
            "merge",
            path,
            "1000",
            "1",
            "1",
            "0",
            "30",
            out_merge,
        ]
    #cmd = (" ".join(command))
    return command


if __name__ == "__main__":
    args = parser.parse_args()
    createfiles(args.vcf1, args.vcf2, args.o1, args.o2)
    cmd = prepare_merge(args.vcf1, args.vcf2)
    print("Succesfully merged")
    print(cmd)