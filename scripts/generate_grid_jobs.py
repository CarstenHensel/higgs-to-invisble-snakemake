#!/usr/bin/env python3
"""
generate_grid_jobs.py

Generate ILCDIRAC grid submission scripts and option files
from a master LFN list and a YAML cross-section file.

- Creates one directory per ProdID
- Writes htoinv_<ProdID>.py (options file)
- Writes submit_<ProdID>.py (job submission script)
- Logs actions to a timestamped log file
- Supports dry run (--dry-run)

Author: Carsten Hensel (auto-generated draft)
"""

import os
import argparse
import yaml
from datetime import datetime
from pathlib import Path

# --- hardcoded global settings
TARGET_LUMI = 1000.0
SANDBOX_PATH = "/eos/user/c/chensel/ILC/KEY4HEP_STAGING/job_sandbox.tgz"
STEERING_BASEDIR = "/afs/cern.ch/user/c/chensel/ILD/workarea/May2025/k4-project-template/options"

def parse_args():
    parser = argparse.ArgumentParser(description="Generate ILCDIRAC submission scripts.")
    parser.add_argument("lfn_file", help="Path to all_files.txt (list of LFNs)")
    parser.add_argument("xsec_file", help="Path to cross-section YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without creating files")
    return parser.parse_args()

def load_inputs(lfn_file, xsec_file):
    # load LFNs
    with open(lfn_file) as f:
        lfns = [line.strip() for line in f if line.strip()]
    # load cross-sections
    with open(xsec_file) as f:
        xsecs = yaml.safe_load(f)
    return lfns, xsecs

def group_lfns_by_prodid(lfns):
    """Extract ProdID from LFN path (pattern .../000<ProdID>/...)"""
    grouped = {}
    for lfn in lfns:
        parts = lfn.split("/")
        for p in parts:
            if p.startswith("000") and p[3:].isdigit():
                prodid = int(p[3:])
                grouped.setdefault(prodid, []).append("LFN:" + lfn.lstrip("/"))
                break
    return grouped

def write_option_file(path, prodid, proc, xsec, nevts):
    content = f"""from Gaudi.Configuration import *
import os
from Configurables import k4DataSvc
from Configurables import HtoInvAlg

evtSvc = k4DataSvc('EventDataSvc')

myalg = HtoInvAlg()
myalg.cross_section = {xsec}
myalg.n_events_generated = {nevts}
myalg.processName = '{proc}'
myalg.processID = {prodid}
myalg.targetLumi = {TARGET_LUMI}
myalg.root_output_file = 'myalg_higgs_to_invisible_{prodid}.root'
myalg.OutputLevel = INFO
"""
    with open(path, "w") as f:
        f.write(content)

def write_submit_file(path, prodid, input_files):
    option_file = f"{STEERING_BASEDIR}/htoinv_{prodid}.py"
    output_files = [f.split("/")[-1].replace(".slcio", "CERN-DST-EOS.slcio") for f in input_files]

    content = f"""from DIRAC.Core.Base import Script
Script.parseCommandLine()

from ILCDIRAC.Interfaces.API.DiracILC import DiracILC
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import UserJob
from ILCDIRAC.Interfaces.API.NewInterface.Applications import GaudiApp

dIlc = DiracILC()
inputFiles = {input_files}
outputFiles = {output_files}

job = UserJob()
job.setName('htoinv_DST_%n')
job.setSplitInputData(inputFiles)
job.setSplitParameter('outputFile', outputFiles)
job.setSplitOutputData([[out] for out in outputFiles],
                       'htoinv/DSTs-{prodid}',
                        'CERN-DST-EOS')
job.setInputSandbox(["{SANDBOX_PATH}"])
job.setOutputSandbox(['*.log'])

gaudi = GaudiApp()
gaudi.setExecutableName("k4run")
gaudi.setVersion("key4hep_nightly")
gaudi.setSteeringFile("{option_file}")
gaudi.setInputFileFlag("--inputFiles")
gaudi.setOutputFileFlag("--outputFile")
gaudi.setOutputFile("%(outputFile)s")
gaudi.setExtraCLIArguments("-n -1")
gaudi.setEnergy(250.0)
job.append(gaudi)

res = job.submit(dIlc, mode="wms")
if res.get("OK"):
    print("Successfully submitted job(s):", res["Value"])
else:
    print("Submission failed:", res)
"""
    with open(path, "w") as f:
        f.write(content)

def main():
    args = parse_args()
    lfns, xsecs = load_inputs(args.lfn_file, args.xsec_file)
    grouped_lfns = group_lfns_by_prodid(lfns)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"job_generation_{timestamp}.log"
    log_lines = []

    for entry in xsecs:
        prodid = entry["ProdID"]
        if prodid not in grouped_lfns:
            continue
        proc = entry["Process"]
        xsec = entry["CrossSection_fb"]
        nevts = entry["NumberOfEvents"]

        outdir = Path(str(prodid))
        opt_path = outdir / f"htoinv_{prodid}.py"
        sub_path = outdir / f"submit_{prodid}.py"

        msg = f"[{timestamp}] ProdID {prodid} ({proc}) → {len(grouped_lfns[prodid])} files"
        print(msg)
        log_lines.append(msg)

        if not args.dry_run:
            outdir.mkdir(parents=True, exist_ok=True)
            write_option_file(opt_path, prodid, proc, xsec, nevts)
            write_submit_file(sub_path, prodid, grouped_lfns[prodid])
    
    if not args.dry_run:
        with open(log_file, "w") as f:
            f.write("\n".join(log_lines))

        # write master submission script
        prodids = [entry["ProdID"] for entry in xsecs if entry["ProdID"] in grouped_lfns]
        master_script = write_master_submit(prodids)
        print(f"Master submission script written: {master_script}")

    if not args.dry_run:
        with open(log_file, "w") as f:
            f.write("\n".join(log_lines))


def write_master_submit(prodid_list):
    """Write a shell script to submit all generated jobs in one go."""
    script_path = Path("submit_all.sh")
    lines = [
        "#!/bin/bash",
        "# Auto-generated master submission script",
        "set -euo pipefail",
        "",
    ]
    for pid in prodid_list:
        lines.append(f"echo 'Submitting ProdID {pid} ...'")
        lines.append(f"python3 {pid}/submit_{pid}.py")
        lines.append("")
    with open(script_path, "w") as f:
        f.write("\n".join(lines))
    os.chmod(script_path, 0o755)
    return script_path


if __name__ == "__main__":
    main()
