rule collect_xsecs:
    input:
        "/afs/cern.ch/user/c/chensel/cernbox/ILC/HtoInv/MC/pilot_lfns.txt"
    output:
        "xsecs.yaml"
    shell:
        "python3 scripts/ilc_xsec_collector.py -i {input} -o {output}"
