#!/usr/bin/env python3
"""
generate_grid_jobs.py

Generate ILCDIRAC grid submission scripts and option files
from a master LFN list and a YAML cross-section file (new format).

- Creates one directory per (GenID, ProdID) combination
- Writes higgsToInvisible_<GenID>_<ProdID>.py (options file)
- Writes submit_grid_<GenID>_<ProdID>.py (job submission script)
- Logs actions to a timestamped log file
- Supports dry run (--dry-run)
"""

import os
import argparse
import yaml
from datetime import datetime
from pathlib import Path
import textwrap
import re

# --- hardcoded global settings
TARGET_LUMI = 1000.0
SANDBOX_PATH = "LFN:/ilc/user/c/chensel/job_sandbox.tgz"
GAUDI_VERSION = "key4hep_250529"

def parse_args():
    parser = argparse.ArgumentParser(description="Generate ILCDIRAC submission scripts.")
    parser.add_argument("lfn_file", help="Path to all_files.txt (list of LFNs)")
    parser.add_argument("xsec_file", help="Path to cross-section YAML file")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without creating files")
    return parser.parse_args()

def load_inputs(lfn_file, xsec_file):
    with open(lfn_file) as f:
        lfns = [line.strip() for line in f if line.strip()]
    with open(xsec_file) as f:
        xsecs = yaml.safe_load(f)
    return lfns, xsecs

def extract_genid_from_lfn(lfn):
    """
    Extract Generator ID (6 digits after '.I') from LFN.
    """
    match = re.search(r'\.I(\d{6})\.', lfn)
    return int(match.group(1)) if match else None

def extract_prodid_from_lfn(lfn):
    """
    Extract Production ID (number after 'd_dst_') from LFN.
    """
    match = re.search(r'd_dst_(\d+)_', lfn)
    return int(match.group(1)) if match else None

def group_lfns_by_genid_prodid(lfns):
    """
    Groups LFNs by (genid, prodid) combination.
    """
    grouped = {}
    for lfn in lfns:
        genid = extract_genid_from_lfn(lfn)
        prodid = extract_prodid_from_lfn(lfn)
        if genid is None or prodid is None:
            continue
        key = (genid, prodid)
        lfn_entry = lfn if lfn.startswith("LFN:") else "LFN:/" + lfn.lstrip("/")
        grouped.setdefault(key, []).append(lfn_entry)
    return grouped

def write_option_file(path: Path, genid: int, prodid: int, proc: str, xsec: float, nevts: int):
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
parser_group.add_argument("--cms", action="store", help="Choose a Centre-of-Mass energy", default=240, choices=(91, 160, 240, 365), type=int)


reco_args = parser.parse_known_args()[0]

# setting up the input
alg_list = []
evt_svc = EventDataSvc("EventDataSvc")
evt_svc.OutputLevel = INFO
svc_list = [evt_svc]
io_svc = IOSvc()

io_handler = IOHandlerHelper(alg_list, io_svc)
io_handler.add_reader(reco_args.inputFiles)


# setting up the Higgs to Invisible algorithm
from Configurables import HtoInvAlg
myalg = HtoInvAlg()
myalg.cross_section = {xsec}
myalg.n_events_generated = {nevts}
myalg.processName = '{proc}'
myalg.processID = {prodid}
myalg.targetLumi = {TARGET_LUMI}
myalg.root_output_file = reco_args.myOutputFile 
myalg.RecoParticleColl = 'PandoraPFOs'
myalg.IsolatedLeptonsColl = 'IsolatedLeptons'
myalg.EventHeaderColl = 'EventHeader'
myalg.MCParticleColl = 'MCParticlesSkimmed'
myalg.JetFinderColl = 'MyJets'
myalg.Outputs = "MET"
myalg.OutputLevel = INFO



# setting up the jet finder
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


#MyJetFinder.EDM4hep2LcioTool = e2lConv
#MyJetFinder.Lcio2EDM4hepTool = l2eConv



# now the isolated lepton tagger

MyIsolatedLeptonTaggingProcessor = MarlinProcessorWrapper("MyIsolatedLeptonTaggingProcessor")
MyIsolatedLeptonTaggingProcessor.OutputLevel = INFO
MyIsolatedLeptonTaggingProcessor.ProcessorType = "IsolatedLeptonTaggingProcessor"
MyIsolatedLeptonTaggingProcessor.Parameters = {{
                                               "CosConeLarge": ["0.95"],
                                               "CosConeSmall": ["0.98"],
                                               "CutOnTheISOElectronMVA": ["2.0"],
                                               "CutOnTheISOMuonMVA": ["0.7"],
                                               "DirOfISOElectronWeights": ["/cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02-03/MarlinReco/v01-32/Analysis/IsolatedLeptonTagging/example/isolated_electron_weights"],
                                               "DirOfISOMuonWeights": ["/cvmfs/ilc.desy.de/sw/x86_64_gcc82_centos7/v02-02-03/MarlinReco/v01-32/Analysis/IsolatedLeptonTagging/example/isolated_muon_weights_woYoke"],
                                               "InputPandoraPFOsCollection": ["PandoraPFOs"],
                                               "InputPrimaryVertexCollection": ["PrimaryVertex"],
                                               "IsSelectingOneIsoLep": ["false"],
                                               "MaxD0SigForElectron": ["50"],
                                               "MaxD0SigForMuon": ["20"],
                                               "MaxEOverPForElectron": ["1.3"],
                                               "MaxEOverPForMuon": ["0.3"],
                                               "MaxZ0SigForElectron": ["50"],
                                               "MaxZ0SigForMuon": ["20"],
                                               "MinEOverPForElectron": ["0.5"],
                                               "MinEecalOverTotEForElectron": ["0.9"],
                                               "MinEyokeForMuon": ["1.2"],
                                               "MinPForElectron": ["5"],
                                               "MinPForMuon": ["5"],
                                               "OutputIsoLeptonsCollection": ["IsolatedLeptons"],
                                               "OutputPFOsWithoutIsoLepCollection": ["PandoraPFOsWithoutIsoLep"],
                                               "UseYokeForMuonID": ["false"]
                                               }}

edm4hep2LcioConv = EDM4hep2LcioTool("EDM4hep2Lcio")
lcio2edm4hepConv = Lcio2EDM4hepTool("Lcio2EDM4hep")
edm4hep2LcioConv.convertAll = False
edm4hep2LcioConv.collNameMapping = {{
        'PrimaryVertex':'PrimaryVertex',
        'PandoraPFOs':'PandoraPFOs',
        "PandoraClusters": "PandoraClusters",
        "MarlinTrkTracks": "MarlinTrkTracks",
        "EventHeader": "EventHeader"
      }}


lcio2edm4hepConv.convertAll = False
lcio2edm4hepConv.collNameMapping = {{
     'PandoraPFOs': 'PandoraPFOs',
     'IsolatedLeptons': 'IsolatedLeptons',
     'PandoraPFOsWithoutIsoLep': 'PandoraPFOsWithoutIsoLep',
     "PandoraClusters": "PandoraClusters",
     "MarlinTrkTracks": "MarlinTrkTracks",
     "EventHeader": "EventHeader",
     "MCParticlesSkimmed": "MCParticlesSkimmed",
     "MyJets": "MyJets",
     "PFOsfromJets": "PFOsfromJets"
     }}




#MyIsolatedLeptonTaggingProcessor.EDM4hep2LcioTool = edm4hep2LcioConv
MyIsolatedLeptonTaggingProcessor.Lcio2EDM4hepTool = lcio2edm4hepConv

MyJetFinder.EDM4hep2LcioTool = edm4hep2LcioConv
MyJetFinder.Lcio2EDM4hepTool = lcio2edm4hepConv

# Lepton Pairing Processor
from Configurables import LeptonPairingAlg

MyLeptonPairing = LeptonPairingAlg()
MyLeptonPairing.RecoParticleColl = 'PandoraPFOs'
MyLeptonPairing.IsolatedLeptonsColl = 'IsolatedLeptons'
MyLeptonPairing.PFOsWOIsoLepColl = 'PandoraPFOsWithoutIsoLep'
MyLeptonPairing.doPhotonRecovery = True
MyLeptonPairing.diLeptinInvariantMass = 91.1876

alg_list.extend([MyIsolatedLeptonTaggingProcessor, MyLeptonPairing, MyJetFinder, myalg])

io_handler.finalize_converters()

from k4FWCore import ApplicationMgr
ApplicationMgr( TopAlg = alg_list,
                EvtSel="NONE",
                EvtMax=-1,
                ExtSvc=[evt_svc],
                OutputLevel=INFO,
               )

'''
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))

def _make_output_filename_from_lfn(lfn: str, genid: int, prodid: int, idx: int):
    return f"myalg_higgs_to_invisible_{genid}_{prodid}_{idx}.root"

def write_submit_file(path: Path, genid: int, prodid: int, proc: str, input_files):
    steering_name = f"higgsToInvisible_{proc}_{genid}_{prodid}.py"
    output_files = [_make_output_filename_from_lfn(inf, genid, prodid, i+1) for i, inf in enumerate(input_files)]
    content = f'''\
from DIRAC.Core.Base import Script
Script.parseCommandLine()

from ILCDIRAC.Interfaces.API.DiracILC import DiracILC
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import UserJob
from ILCDIRAC.Interfaces.API.NewInterface.Applications import GaudiApp

dIlc = DiracILC()
inputFiles = {input_files}
outputFiles = {output_files}

job = UserJob()
job.setName("htoinv_DST_%n")


# 1) Split input
#job.setInputData(inputFiles)
chunk_size = min(20, len(inputFiles))
job.setSplitInputData(inputFiles, numberOfFilesPerJob=chunk_size)

# 2) Output files
job.setOutputData(
    ["myalg_higgs_to_invisible_{proc}_{genid}_{prodid}.root"],
    OutputPath="htoinv/ROOT-{proc}-{genid}-{prodid}",
    OutputSE="CERN-DST-EOS"
)


# 3) Gaudi
gaudi = GaudiApp()
gaudi.setExecutableName("k4run")
gaudi.setVersion("key4hep_250529")
gaudi.setInputFileFlag("--inputFiles")
gaudi.setInputFile("%(InputData)s")
gaudi.setOutputFile("myalg_higgs_to_invisible_{proc}_{genid}_{prodid}.root")
gaudi.setOutputFileFlag("--myOutputFile")
gaudi.setNumberOfEvents(-1)
gaudi.setSteeringFile("{steering_name}")


# 4) Append after input/output are set
job.append(gaudi)

# 5) Sandboxes
job.setOutputSandbox(["*.log", "*.out", "*.err"])

job.setInputSandbox(["{SANDBOX_PATH}", "{steering_name}"])

job.dontPromptMe()


res = job.submit(dIlc, mode="wms")
#res = job.submit(dIlc, mode="local")

if res.get("OK"):
    print("Successfully submitted job(s):", res["Value"])
else:
    print("Submission failed:", res)
'''
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content))

def write_master_submit(job_keys):
    script_path = Path("submit_all.sh")
    lines = ["#!/bin/bash", "# Auto-generated master submission script", "set -euo pipefail", ""]
    for genid, prodid in job_keys:
        lines.append(f"echo 'Submitting GenID {genid}, ProdID {prodid} ...'")
        lines.append(f"cd {genid}_{prodid}/")
        lines.append(f"python3 submit_grid_{genid}_{prodid}.py")
        lines.append(f"cd ../")
        lines.append(f"sleep 10\n")
    with open(script_path, "w") as f:
        f.write("\n".join(lines))
    os.chmod(script_path, 0o755)
    return script_path

def main():
    args = parse_args()
    lfns, xsecs = load_inputs(args.lfn_file, args.xsec_file)
    grouped_lfns = group_lfns_by_genid_prodid(lfns)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"job_generation_{timestamp}.log"
    log_lines = []
    job_keys = []

    for entry in xsecs:
        genid = entry.get("GeneratorID", -1)
        proc = entry.get("Process", "unknown_proc")
        xsec = entry.get("CrossSection_fb", 0.0)
        nevts = entry.get("NumberOfEvents", 0)
        prod_ids = entry.get("ProductionIDs", [])

        for prodid in prod_ids:
            key = (genid, prodid)
            if key not in grouped_lfns:
                msg = f"[{timestamp}] GenID {genid}, ProdID {prodid} not found in LFN list - skipping"
                print(msg)
                log_lines.append(msg)
                continue

            outdir = Path(f"{genid}_{prodid}")
            opt_path = outdir / f"higgsToInvisible_{proc}_{genid}_{prodid}.py"
            sub_path = outdir / f"submit_grid_{proc}_{genid}_{prodid}.py"

            msg = f"[{timestamp}] Process {proc}. GenID {genid}, ProdID {prodid} ({proc}) → {len(grouped_lfns[key])} files"
            print(msg)
            log_lines.append(msg)

            if not args.dry_run:
                outdir.mkdir(parents=True, exist_ok=True)
                write_option_file(opt_path, genid, prodid, proc, xsec, nevts)
                write_submit_file(sub_path, genid, prodid, proc, grouped_lfns[key])
                job_keys.append(key)

    if not args.dry_run and job_keys:
        with open(log_file, "w") as f:
            f.write("\n".join(log_lines))
        master_script = write_master_submit(job_keys)
        print(f"Master submission script written: {master_script}")

    print("Done. Log lines:")
    print("\n".join(log_lines))

if __name__ == "__main__":
    main()
