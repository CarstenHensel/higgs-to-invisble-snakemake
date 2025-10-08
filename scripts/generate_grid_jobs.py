#!/usr/bin/env python3
"""
generate_grid_jobs.py

Generate ILCDIRAC grid submission scripts and option files
from a master LFN list and a YAML cross-section file.

- Creates one directory per ProdID
- Writes higgsToInvisible_<ProdID>.py (options file, new format)
- Writes submit_grid_<ProdID>.py (job submission script, new format)
- Logs actions to a timestamped log file
- Supports dry run (--dry-run)

Author: Carsten Hensel (adapted)
"""
import os
import argparse
import yaml
from datetime import datetime
from pathlib import Path
import textwrap

# --- hardcoded global settings
TARGET_LUMI = 1000.0
# Keep SANDBOX_PATH as earlier (used in example submit_grid.py)
SANDBOX_PATH = "LFN:/ilc/user/c/chensel/job_sandbox.tgz"
# steering base directory used only if needed in the old workflow; not used for new per-prod option files
STEERING_BASEDIR = "/afs/cern.ch/user/c/chensel/ILD/workarea/May2025/k4-project-template/options"

GAUDI_VERSION = "key4hep_250529"


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
            # detect section like '00015420' -> ProdID 15420
            if p.startswith("000") and p[3:].isdigit():
                prodid = int(p[3:])
                # keep the LFN formatting used by ILCDIRAC (prepend 'LFN:' if needed)
                lfn_entry = lfn if lfn.startswith("LFN:") else "LFN:" + lfn.lstrip("/")
                grouped.setdefault(prodid, []).append(lfn_entry)
                break
    return grouped


def write_option_file(path: Path, prodid: int, proc: str, xsec: float, nevts: int):
    """
    Create a higgsToInvisible_<ProdID>.py file following the new format.
    The file uses the same argument parser style as your example and expects
    --inputFiles and --myOutputFile.
    """
    content = f'''\
from Gaudi.Configuration import *
import os
import sys
sys.path.insert(1, os.path.join(os.getcwd(), 'python'))

from Configurables import k4DataSvc
from Configurables import MarlinProcessorWrapper, EDM4hep2LcioTool, Lcio2EDM4hepTool
from Configurables import EventDataSvc
from k4FWCore import IOSvc
from k4MarlinWrapper.io_helpers import IOHandlerHelper
from k4FWCore.parseArgs import parser

parser_group = parser.add_argument_group("higgsToInvisible custom options")
parser_group.add_argument("--inputFiles", action="extend", nargs="+", metavar=("file1", "file2"), help="One or multiple input files")
parser_group.add_argument("--myOutputFile", type=str, help="Output file name")
# keep existing example switches available
parser_group.add_argument("--cms", action="store", help="Choose a Centre-of-Mass energy", default=240, choices=(91, 160, 240, 365), type=int)

reco_args = parser.parse_known_args()[0]

print("arguments --------------------> ", reco_args)

# setting up the input
alg_list = []
evt_svc = EventDataSvc("EventDataSvc")
evt_svc.OutputLevel = INFO
svc_list = [evt_svc]
io_svc = IOSvc()

io_handler = IOHandlerHelper(alg_list, io_svc)
# accept None gracefully
if getattr(reco_args, "inputFiles", None):
    io_handler.add_reader(reco_args.inputFiles)

from Configurables import HtoInvAlg
myalg = HtoInvAlg()
myalg.cross_section = {xsec}
myalg.n_events_generated = {nevts}
myalg.processName = '{proc}'
myalg.processID = {prodid}
myalg.targetLumi = {TARGET_LUMI}
# let steering take the runtime --myOutputFile value
myalg.root_output_file = getattr(reco_args, "myOutputFile", "myalg_higgs_to_invisible_{prodid}.root")
# populate commonly used collections (kept from example)
myalg.RecoParticleColl = 'PandoraPFOs'
myalg.IsolatedLeptonsColl = 'IsolatedLeptons'
myalg.EventHeaderColl = 'EventHeader'
myalg.MCParticleColl = 'MCParticlesSkimmed'
myalg.JetFinderColl = 'MyJets'
myalg.Outputs = "MET"
myalg.OutputLevel = INFO

# Example additional processors from your template (kept minimal)
MyJetFinder = MarlinProcessorWrapper("MyJetFinder")
MyJetFinder.ProcessorType = "FastJetProcessor"
MyJetFinder.Parameters = {{
    "algorithm": ["ValenciaPlugin", "1.2", "1.0", "0.7"],
    "clusteringMode": ["ExclusiveNJets", "2"],
    "jetOut": ["MyJets"],
    "recParticleIn": ["PandoraPFOs"],
    "recParticleOut": ["PFOsFromJets"],
    "recombinationScheme": ["E_scheme"],
    "storeParticlesInJets": ["true"],
}}
MyJetFinder.OutputLevel = INFO

# Converters (kept from example; non-exhaustive)
e2lConv = EDM4hep2LcioTool("EDM4hep2Lcio")
l2eConv = Lcio2EDM4hepTool("Lcio2EDM4hep")
e2lConv.convertAll = False
e2lConv.collNameMapping = {{
        'PrimaryVertex':'PrimaryVertex',
        'PandoraPFOs':'PandoraPFOs',
        "PandoraClusters": "PandoraClusters",
        "MarlinTrkTracks": "MarlinTrkTracks",
        "EventHeader": "EventHeader",
        "MCParticlesSkimmed": "MCParticlesSkimmed"
}}

l2eConv.convertAll = False
l2eConv.collNameMapping = {{
     'PandoraPFOs': 'PandoraPFOs',
     'MyJets': 'MyJets',
     'PFOsFromJets': 'PFOsFromJets',
     "PandoraClusters": "PandoraClusters",
     "MarlinTrkTracks": "MarlinTrkTracks",
     "EventHeader": "EventHeader",
     "MCParticlesSkimmed": "MCParticlesSkimmed"
}}

e2lConv.OutputLevel = INFO
l2eConv.OutputLevel = INFO

# Add processors and the main algorithm
alg_list.extend([MyJetFinder, myalg])

# finalize converters if IO handler exists
try:
    io_handler.finalize_converters()
except Exception:
    pass

from k4FWCore import ApplicationMgr
ApplicationMgr( TopAlg = alg_list,
                EvtSel="NONE",
                # default: process all events; steering/gaudi may override via CLI
                EvtMax=-1,
                ExtSvc=[evt_svc],
                OutputLevel=INFO,
               )
'''
    # write to file
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))


def _make_output_filename_from_lfn(lfn: str, prodid: int, idx: int):
    """
    Create a short, deterministic ROOT filename from an input LFN.
    e.g. LFN:/.../something.slcio -> myalg_higgs_to_invisible_<prodid>_<idx>.root
    """
    # strip leading LFN: if present
    raw = lfn.split("LFN:")[-1]
    basename = raw.split("/")[-1]
    # remove extension if any
    stem = basename.split(".")[0]
    return f"myalg_higgs_to_invisible_{prodid}_{idx}.root"


def write_submit_file(path: Path, prodid: int, input_files):
    """
    Create a submit_grid_<ProdID>.py script following the structure of your
    example submit_grid.py but enabling splitting across input files.
    """
    # steering file name we wrote for this prodid
    steering_name = f"higgsToInvisible_{prodid}.py"

    # construct output file names mapped to inputs
    output_files = []
    for i, inf in enumerate(input_files, start=1):
        output_files.append(_make_output_filename_from_lfn(inf, prodid, i))

    # prepare the python content
    content = f'''\
from DIRAC.Core.Base import Script
Script.parseCommandLine()

from ILCDIRAC.Interfaces.API.DiracILC import DiracILC
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import UserJob
from ILCDIRAC.Interfaces.API.NewInterface.Applications import GaudiApp

# --- DIRAC instance
dIlc = DiracILC()

# --- input files
inputFiles = {input_files}

# --- output files (one per input)
outputFiles = {output_files}

# --- create job
job = UserJob()
job.setName("htoinv_DST_%n")
job.setSplitInputData(inputFiles)

# Tell Gaudi how many events to process per job: -1 means 'all'
gaudi = GaudiApp()
gaudi.setExecutableName("k4run")
gaudi.setVersion("{GAUDI_VERSION}")
gaudi.setInputFileFlag("--inputFiles")
gaudi.setOutputFileFlag("--myOutputFile")

# We'll supply the per-job output file name via splitting parameter
# default (when not split) fallback:
gaudi.setOutputFile(outputFiles[0] if outputFiles else "myalg_higgs_to_invisible_{prodid}.root")
# process all events by default (can be overridden)
gaudi.setNumberOfEvents(-1)

# steering file (must be available in the input sandbox)
gaudi.setSteeringFile("{steering_name}")

job.append(gaudi)

# Map split parameter 'myOutputFile' to the per-input output files
job.setSplitParameter('myOutputFile', outputFiles)

# declare physics outputs to SE (one file per job)
job.setSplitOutputData([[out] for out in outputFiles],
                       "htoinv/ROOT-{prodid}",
                       "CERN-DST-EOS")

# Local tarball with build + steering file
job.setInputSandbox([
    "{SANDBOX_PATH}",
    "{steering_name}"
])

# Logs to your local machine
job.setOutputSandbox(["*.log", "*.out", "*.err"])

# append gaudi already done above; don't prompt at submit time
job.dontPromptMe()

# submit with confirmation
res = job.submit(dIlc, mode="wms")

if res.get("OK"):
    print("Successfully submitted job(s):", res["Value"])
else:
    print("Submission failed:", res)
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))


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
        lines.append(f"python3 {pid}/submit_grid_{pid}.py")
        lines.append("")
    with open(script_path, "w") as f:
        f.write("\n".join(lines))
    os.chmod(script_path, 0o755)
    return script_path


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
            msg = f"[{timestamp}] ProdID {prodid} not found in LFN list - skipping"
            print(msg)
            log_lines.append(msg)
            continue
        proc = entry.get("Process", f"proc_{prodid}")
        xsec = entry.get("CrossSection_fb", 0.0)
        nevts = entry.get("NumberOfEvents", 0)

        outdir = Path(str(prodid))
        opt_path = outdir / f"higgsToInvisible_{prodid}.py"
        sub_path = outdir / f"submit_grid_{prodid}.py"

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

    # also print summary to stdout
    print("Done. Log lines:")
    print("\n".join(log_lines))


if __name__ == "__main__":
    main()
