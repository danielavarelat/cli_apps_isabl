"""QC data constants."""

BASE_APPLICATION_RESULTS = {
    "multiqc_html": {
        "frontend_type": "html",
        "description": "MultiQC Report.",
        "verbose_name": "Quality Control Report",
        "external_link": "https://multiqc.info/docs/#using-multiqc-reports",
    },
    "multiqc_data": {
        "frontend_type": "text-file",
        "description": "MultiQC json file.",
        "verbose_name": "MultiQC JSON File",
    },
    "multiqc_stats": {
        "optional": True,
        "frontend_type": "text-file",
        "description": "Statistics collected by MultiQC.",
        "verbose_name": "MultiQC Statistics",
    },
}

APPLICATION_RESULTS = dict(
    read_length={
        "frontend_type": "number",
        "description": "Read length as reported by Picard (DNA) and RNASEQC (RNA).",
        "verbose_name": "Read Length",
    },
    **BASE_APPLICATION_RESULTS
)


# base picard commands
PICARD_BASE_COMMANDS = [
    (
        "CollectAlignmentSummaryMetrics "
        "REFERENCE_SEQUENCE={reference} "
        "INPUT={bampath} "
        "OUTPUT={outbase}_alignment_summary_metrics.txt "
    ),
    (
        "CollectInsertSizeMetrics "
        "INPUT={bampath} "
        "OUTPUT={outbase}_insert_size_metrics.txt "
        "HISTOGRAM_FILE={outbase}_insert_size_histogram.pdf "
        "MINIMUM_PCT=0.05 "
    ),
    (
        "CollectGcBiasMetrics "
        "REFERENCE_SEQUENCE={reference} "
        "INPUT={bampath} "
        "OUTPUT={outbase}_gc_bias_metrics.txt "
        "CHART={outbase}_gc_bias_metrics.pdf "
        "SUMMARY_OUTPUT={outbase}_summary_metrics.txt "
    ),
]

# picard commands for targeted data
PICARD_TARGETED_COMMANDS = [
    ("CreateSequenceDictionary " "R={reference} " "OUTPUT={outbase}_reference.dict "),
    (
        "BedToIntervalList "
        "INPUT={bedfile} "
        "OUTPUT={outbase}.interval_list "
        "SEQUENCE_DICTIONARY={outbase}_reference.dict "
    ),
    (
        "CollectHsMetrics "
        "R={reference} "
        "INPUT={bampath} "
        "OUTPUT={outbase}_hs_metrics.txt "
        "BAIT_INTERVALS={outbase}.interval_list "
        "TARGET_INTERVALS={outbase}.interval_list "
    ),
    (
        "CollectSequencingArtifactMetrics "
        "R={reference} "
        "INPUT={bampath} "
        "OUTPUT={outbase}_artifact_metrics "
    ),
]
