# rules/lcio_conversion.smk

rule convert:
    input:
        config["slcio_path"]
    output:
        f"{config['slcio_path']}/.conversion_done"
    params:
        opts = config.get("slcio_conversion_options", "")
    shell:
        """
        python scripts/slcio2edm4hep_validate_crawler.py {params.opts} {input}
        touch {output}
        """


