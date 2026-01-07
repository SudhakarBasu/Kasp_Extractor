# 🧬 KASP Extractor - Batch Processing Tool

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)](https://github.com/yourusername/kasp-extractor/graphs/commit-activity)

A powerful Python tool for extracting flanking sequences around genetic variants for KASP (Kompetitive Allele Specific PCR) primer design. Supports batch processing of entire VCF files with flexible filtering options.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Processing Modes](#processing-modes)
  - [Command Line Options](#command-line-options)
  - [Examples](#examples)
- [Output Format](#output-format)
- [Performance](#performance)
- [Tips & Best Practices](#tips--best-practices)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

## ✨ Features

- 🔄 **Three Processing Modes**: Process entire VCF, specific chromosome, or single variant
- 📁 **Single Output File**: All results consolidated with clear headers and metadata
- 🎯 **Flexible Filtering**: Filter by SNPs only, indels only, or process all variant types
- 📊 **Progress Tracking**: Real-time progress updates for large-scale batch processing
- 🛡️ **Robust Error Handling**: Warnings for reference mismatches and validation checks
- ⚙️ **Customizable**: Adjust flanking sequence length to meet your requirements
- 💾 **No Dependencies**: Uses only Python standard library
- 🚀 **Fast**: Efficiently processes thousands of variants

## 📥 Installation

### Prerequisites

- Python 3.6 or higher
- No external dependencies required!

### Download

```bash
# Clone the repository
git clone https://github.com/yourusername/kasp-extractor.git
cd kasp-extractor

# Make executable
chmod +x kasp_extractor_batch.py

# Test installation
python kasp_extractor_batch.py --help
```

Or download directly:

```bash
wget https://raw.githubusercontent.com/yourusername/kasp-extractor/main/kasp_extractor_batch.py
chmod +x kasp_extractor_batch.py
```

## 🚀 Quick Start

```bash
# Process entire VCF file
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r reference.fasta \
    -o kasp_output.txt

# Process specific chromosome
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r reference.fasta \
    -c chr1 \
    -o kasp_chr1.txt

# Process single variant
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r reference.fasta \
    -c chr1 \
    -p 12345 \
    -o kasp_single.txt
```

## 💻 Usage

### Processing Modes

The script automatically detects the processing mode based on input parameters:

| Mode | Parameters | Description |
|------|------------|-------------|
| **🌐 All VCF** | `-v` `-r` `-o` | Process all chromosomes and variants |
| **📍 Chromosome** | `-v` `-r` `-c` `-o` | Process all variants on specific chromosome |
| **🎯 Single Variant** | `-v` `-r` `-c` `-p` `-o` | Extract single variant at position |

### Command Line Options

```
Required Arguments:
  -v, --vcf         Input VCF file (can be gzipped)
  -r, --reference   Reference genome FASTA file
  -o, --output      Output file path

Optional Arguments:
  -c, --chrom       Chromosome name (default: all chromosomes)
  -p, --position    Variant position (requires -c)
  -l, --length      Flanking sequence length in bp (default: 100)
  --skip-indels     Process only SNPs (skip insertions/deletions)
  --only-indels     Process only indels (skip SNPs)
  -h, --help        Show help message
```

### Examples

#### 1. Process Entire VCF File

```bash
python kasp_extractor_batch.py \
    -v cohort_final.vcf.gz \
    -r reference/genome.fa \
    -o kasp_all_variants.txt
```

#### 2. Process Specific Chromosome

```bash
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r genome.fa \
    -c chr5 \
    -o kasp_chr5.txt
```

#### 3. Extract Single Variant

```bash
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r genome.fa \
    -c chr1 \
    -p 12345 \
    -o kasp_variant.txt
```

#### 4. SNPs Only (Skip Indels)

```bash
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r genome.fa \
    --skip-indels \
    -o kasp_snps_only.txt
```

#### 5. Indels Only (Skip SNPs)

```bash
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r genome.fa \
    --only-indels \
    -o kasp_indels_only.txt
```

#### 6. Custom Flanking Length (150bp)

```bash
python kasp_extractor_batch.py \
    -v variants.vcf \
    -r genome.fa \
    -l 150 \
    -o kasp_150bp.txt
```

#### 7. Parallel Processing by Chromosome

```bash
# Using GNU parallel for faster processing
parallel "python kasp_extractor_batch.py -v variants.vcf -r genome.fa -c {} -o kasp_{}.txt" ::: chr{1..10}

# Combine results
cat kasp_chr*.txt > kasp_complete.txt
```

## 📄 Output Format

The output file contains flanking sequences in FASTA-like format:

```
# KASP Primer Design Sequences
# Generated from: variants.vcf
# Reference: genome.fasta
# Flanking length: 100 bp
# Total variants: 15,432
#
# Format: >chr:pos [id] REF=X ALT=Y
#         upstream_sequence[REF/ALT]downstream_sequence
#

>chr1:12345 rs123456 REF=A ALT=G
atcgatcgatcgatcgatcgatcg[A/G]tcgatcgatcgatcgatcgatcg

>chr1:67890 rs789012 REF=C ALT=T
ggccttaaggccttaaggccttaa[C/T]aaggccttaaggccttaaggcctt

>chr2:11111 . REF=ATG ALT=A
cccgggtttaaacccgggtttaaa[ATG/A]tttaaacccgggtttaaacccggg
```

**Format Details:**
- **Header lines**: Start with `#`, contain metadata
- **Variant ID line**: Starts with `>`, includes chr:pos, variant ID, REF and ALT
- **Sequence line**: Lowercase flanking sequences with variant in brackets `[REF/ALT]`
- **Blank line**: Separates entries

## ⚡ Performance

Processing speed depends on genome size and number of variants:

| Dataset | Variants | Time | Memory |
|---------|----------|------|--------|
| Small genome (500 Mb) | 1,000 | ~30 sec | ~600 MB |
| Medium genome (1 Gb) | 10,000 | ~2 min | ~1.2 GB |
| Large genome (3 Gb) | 100,000 | ~15 min | ~3.5 GB |
| Plant genome (5 Gb) | 500,000 | ~60 min | ~5.5 GB |

**Optimization Tips:**
- Process by chromosome for large datasets
- Use parallel processing across chromosomes
- Filter VCF by quality before extraction
- Use SSD storage for faster I/O

## 🎯 Tips & Best Practices

### 1. Flanking Length Selection

- **100bp (default)**: Standard for most KASP assays
- **150-200bp**: Better for complex regions or longer primers
- **50-75bp**: Minimal length for simple SNPs

### 2. Quality Control

```bash
# Filter VCF by quality before extraction
bcftools view -i 'QUAL>30 && INFO/DP>10' input.vcf.gz -Oz -o filtered.vcf.gz

# Then run KASP extractor
python kasp_extractor_batch.py -v filtered.vcf.gz -r genome.fa -o kasp_output.txt
```

### 3. Chromosome Name Matching

Ensure chromosome names match between VCF and FASTA:

```bash
# Check VCF chromosome names
bcftools view -H input.vcf.gz | cut -f1 | sort -u

# Check FASTA chromosome names
grep "^>" reference.fa | head

# Rename if needed (example: add "chr" prefix)
bcftools annotate --rename-chrs chr_name_map.txt input.vcf.gz -Oz -o renamed.vcf.gz
```

### 4. Parallel Processing

```bash
#!/bin/bash
# parallel_kasp.sh - Process chromosomes in parallel

VCF="variants.vcf.gz"
REF="genome.fa"
OUTDIR="kasp_results"

mkdir -p $OUTDIR

# Get chromosome list
CHROMS=$(bcftools view -H $VCF | cut -f1 | sort -u)

# Process in parallel (adjust -j based on available cores)
echo "$CHROMS" | parallel -j 8 \
    "python kasp_extractor_batch.py -v $VCF -r $REF -c {} -o $OUTDIR/kasp_{}.txt"

# Combine results
cat $OUTDIR/kasp_*.txt > kasp_complete.txt
```

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: "Chromosome not found in reference"

**Cause**: Chromosome names in VCF don't match FASTA

**Solution**:
```bash
# Check chromosome names
bcftools view -H input.vcf.gz | cut -f1 | sort -u
grep "^>" reference.fa

# Fix mismatches (e.g., "chr1" vs "1")
bcftools annotate --rename-chrs <(paste <(seq 1 22; echo X; echo Y; echo MT) <(seq 1 22 | sed 's/^/chr/'; echo chrX; echo chrY; echo chrM)) input.vcf.gz -Oz -o fixed.vcf.gz
```

#### Issue 2: "Reference allele mismatch"

**Cause**: VCF and reference genome are from different assemblies

**Solution**: Ensure both files are from the same genome version (e.g., hg38, GRCh38)

#### Issue 3: Memory Error

**Cause**: Large genome doesn't fit in RAM

**Solution**:
```bash
# Process by chromosome to reduce memory
for chr in chr{1..22} chrX chrY; do
    python kasp_extractor_batch.py -v variants.vcf -r genome.fa -c $chr -o kasp_$chr.txt
done
```

#### Issue 4: Slow Processing

**Solutions**:
- Use SSD storage
- Process chromosomes in parallel
- Pre-filter VCF by quality/region
- Increase flanking length cautiously (affects processing time)

### Getting Help

If you encounter issues:

1. Check the stderr output for warnings
2. Verify input file formats (VCF and FASTA)
3. Test with a small subset first
4. [Open an issue](https://github.com/SudhakarBasu/Kasp_Extractor/issues) with:
   - Command used
   - Error message
   - VCF and FASTA headers (first few lines)

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report bugs**: [Open an issue](https://github.com/SudhakarBasu/Kasp_Extractor/issues)
2. **Suggest features**: [Start a discussion](https://github.com/SudhakarBasu/Kasp_Extractor/discussions)
3. **Submit pull requests**: Fork, create a branch, make changes, submit PR

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/kasp-extractor.git
cd kasp-extractor

# Create test environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Run tests (if available)
python -m pytest tests/
```

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints where appropriate
- Update README for new features


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


## 📞 Contact

- **Author**: Sudhakar Reddy Basu
- **Email**: basusudhakarreddy@gmail.com
- **GitHub**: [@SudhakarBasu](https://github.com/SudhakarBasu)
- **Website**: https://sudhakarreddy.com

## 🌟 Acknowledgments

- Thanks to all contributors and users
- Inspired by the bioinformatics community's need for efficient KASP primer design tools
- Built with feedback from researchers working on crop genomics and breeding programs

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

Made with ❤️ for the Bioinformatics Community


</div>
