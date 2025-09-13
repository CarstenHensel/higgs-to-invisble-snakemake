#!/usr/bin/env python3
import os
import argparse

def link_edm4hep_files(root_dir, target_dir):
    """
    Recursively find .root files under root_dir and create symbolic links in target_dir.
    """
    os.makedirs(target_dir, exist_ok=True)
    
    count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(".root"):
                src = os.path.join(dirpath, fname)
                dst = os.path.join(target_dir, fname)
                
                try:
                    if not os.path.exists(dst):
                        os.symlink(src, dst)
                        print(f"Linked: {src} -> {dst}")
                        count += 1
                    else:
                        print(f"Skipped (already exists): {dst}")
                except OSError as e:
                    print(f"Error linking {src} -> {dst}: {e}")
    
    print(f"Done. {count} files linked.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Link EDM4hep .root files to Snakemake directory")
    parser.add_argument("root_dir", help="Root directory to search for .root files")
    parser.add_argument("target_dir", help="Snakemake edm4hep directory where links will be created")
    args = parser.parse_args()
    
    link_edm4hep_files(args.root_dir, args.target_dir)
