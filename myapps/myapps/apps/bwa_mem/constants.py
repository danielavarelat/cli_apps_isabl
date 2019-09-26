APPLICATION_DESCRIPTION = """
BWA MEM pipeline as implemented by PCAP-Core.

<br><br>Runs 'BWA mem' method of mapping. Processes multiple lanes, merges, marks
duplicates and provides completed sample BAM/CRAM file including index and md5.
Input can be paired-fastq, interleaved-fastq, BAM or CRAM. Using BAM/CRAM as input is
preferred and will allow header information to be transferred
(important for library tracking in duplicate removal).
"""

APPLICATION_RESULTS = {
    "bam": {
        "frontend_type": "igv_bam:bai",
        "description": "bwa mem aligned reads.",
        "verbose_name": "Bam",
    },
    "bai": {
        "frontend_type": None,
        "description": "bam file index.",
        "verbose_name": "Bai",
    },
    "bas": {
        "frontend_type": "text-file",
        "description": "Alignment statistics.",
        "verbose_name": "Bas",
    },
    "md5": {
        "frontend_type": "string",
        "description": "Bam checksum.",
        "verbose_name": "md5",
    },
    "met": {
        "frontend_type": "text-file",
        "description": "Alignment metrics.",
        "verbose_name": "Bam Metrics",
    },
}
