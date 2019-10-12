import testcircos

#CON LOS DATOS DE PRUEBA DEL TOIL CIRCOS
# ide="testdata"
# cns="/home/danielavt/toil_circosigv/tests/data/empty.cns"
# merged_vcf="/home/danielavt/toil_circosigv/tests/data/subset.vcf"
# bam_file="test_s1.bam"
# ref_gene="/home/danielavt/toil_circosigv/tests/data/circos_genes.bed"
# out_dir="/home/danielavt/testing"

#sampl=testcircos.Sample(ide,cns,merged_vcf,bam_file,ref_gene,out_dir)
#sampl.runcircos()

#CON DEMO DATA
ide="db"
cns="/home/danielavt/toil_circosigv/tests/data/empty.cns"
merged_vcf="/home/danielavt/testing/merged_cloud.vcf"
bam_file=""
ref_gene="/home/danielavt/toil_circosigv/tests/data/circos_genes.bed"
out_dir="/home/danielavt/testing"

sampl=testcircos.Sample(ide,cns,merged_vcf,bam_file,ref_gene,out_dir)
sampl.runcircos()