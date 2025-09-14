# rules/lcio_conversion.smk

rule convert:
    input:
        "/afs/cern.ch/user/c/chensel/cernbox/ILC/HtoInv/MC/pilot_samples/"
    output:
        "/afs/cern.ch/user/c/chensel/cernbox/ILC/HtoInv/MC/pilot_samples/"
    shell:
        """
        python3 scripts/slcio2edm4hep_validate_crawler.py {input} 
