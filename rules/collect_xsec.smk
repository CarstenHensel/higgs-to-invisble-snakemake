rule collect_xsecs:
    input:
        "lfns.txt"
    output:
        "xsecs.yaml"
    shell:
        "./ilc_xsec_collector.py -i {input} -o {output}"
