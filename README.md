# Higgs → Invisible Snakemake Workflow

This repository contains a Snakemake workflow for the Higgs → Invisible analysis at ILD.  
It tracks analysis code, configurations, and small helper files while keeping large datasets and outputs separate.  

---

## Repository Structure

htoinv/
|-- README.md
|-- Snakefile         # Snakemake workflow rules
|-- config.yaml       # Analysis configurations and bookkeeping
|-- data              # Small helper files (metadata, lookup tables)
|-- edm4hep           # Converted EDM4hep files (outputs; ignored)
|-- ntuples           # ROOT ntuples (outputs; ignored)
|-- plots             # Analysis plots (outputs; ignored)
`-- scripts           # Python scripts for conversions and analysis

---

## Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:yourusername/htoinv_snakemake.git
cd htoinv_snakemake

# 2. Set up Python environment

The workflow requires Python >= 3.12 and Snakemake. We recommend using __Miniconda__:

```
# Activate base conda
source ~/miniconda/bin/activate

# Create environment
conda create -n htoinv_snake python=3.12 -y
conda activate htoinv_snake

# Install Snakemake
pip install --user snakemake
```


# 3. Prepare input datasets
- Place large LCIO input files in samples/ as direct copies or symlinks to EOS/AFS:
<ln -s /eos/ilc/MC/Pqqh.slcio samples/Pqqh.slcio>

- The workflow will read files from samples/ automatically.

# 4. Update configuration

Edit config.yaml to list datasets, transformations, and parameters.
Example:

```
datasets:
  Pqqh:
    version: rv02-02-01
    path: samples/Pqqh.slcio
    cross_section: 0.5

transformations:
  convert:
    script: scripts/convert_lcio.py
    output_dir: edm4hep
  analysis:
    script: scripts/analysis.py
    output_dir: ntuples
```

# 5. Run the workflow
```
conda activate htoinv_snake
snakemake -j 4
```

- Snakemake will run:
	- Conversion of LCIO to edm4hep files
	- Analysis scripts producing ROOT ntuples
	- Additional rules (plots, summaries) if added


# 6. Outputs

EDM4hep files -> edm4hep/
ROOT ntuples  -> ntuples/
plots andd summary tables -> plots/

These directories are ignored by Git to keep the repository lightweight.

# 7. Adding new datasets
- Add the dataset to config.yaml.
- Place or symlink the corresponding LCIO file in samples/.
- Run:

```
snakemake -j 4
```

# 8. Contributing

- Update scripts in scripts/ or configuration in config.yaml.
- Add smaller helper files to data/ if needed.
- Commit changes and push:

```
git add scripts/ config.yaml data/
git commit -m "Describe changes"
git push
```

- Do __not__ commit large input/output files.


# 9. Notes
- Unset PYTHONPATH when using Miniconda to avoid conflicts:
```
unset PYTHONPATH
```





