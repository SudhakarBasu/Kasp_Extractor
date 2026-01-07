#!/usr/bin/env python3
"""
Extract flanking sequences around variants for KASP primer design
Supports batch processing of entire VCF or specific chromosome

Usage Examples:
  # Process entire VCF
  python kasp_extractor_batch.py -v variants.vcf -r reference.fasta -o kasp_output.txt
  
  # Process specific chromosome
  python kasp_extractor_batch.py -v variants.vcf -r reference.fasta -c chr1 -o kasp_chr1.txt
  
  # Process specific variant
  python kasp_extractor_batch.py -v variants.vcf -r reference.fasta -c chr1 -p 12345 -o kasp_single.txt
  
  # Custom flank length
  python kasp_extractor_batch.py -v variants.vcf -r reference.fasta -l 150 -o kasp_output.txt
"""

import argparse
import sys
from collections import defaultdict

def parse_fasta(fasta_file):
    """Parse FASTA file and return dictionary of sequences"""
    print("Loading reference genome...", file=sys.stderr)
    sequences = {}
    current_chr = None
    current_seq = []
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_chr:
                    sequences[current_chr] = ''.join(current_seq)
                    print(f"  Loaded {current_chr}: {len(sequences[current_chr]):,} bp", file=sys.stderr)
                current_chr = line[1:].split()[0]
                current_seq = []
            else:
                current_seq.append(line.upper())
        
        if current_chr:
            sequences[current_chr] = ''.join(current_seq)
            print(f"  Loaded {current_chr}: {len(sequences[current_chr]):,} bp", file=sys.stderr)
    
    print(f"Total chromosomes loaded: {len(sequences)}", file=sys.stderr)
    return sequences

def parse_vcf_variants(vcf_file, chrom=None, pos=None):
    """
    Extract variant information from VCF file
    
    Args:
        vcf_file: Path to VCF file
        chrom: Specific chromosome (None = all chromosomes)
        pos: Specific position (None = all positions)
    
    Returns:
        List of variant dictionaries
    """
    variants = []
    skipped = 0
    
    print("Parsing VCF file...", file=sys.stderr)
    
    with open(vcf_file, 'r') as f:
        for line in f:
            # Skip header lines
            if line.startswith('#'):
                continue
            
            fields = line.strip().split('\t')
            if len(fields) < 5:
                skipped += 1
                continue
            
            vcf_chrom = fields[0]
            vcf_pos = int(fields[1])
            variant_id = fields[2]
            ref = fields[3]
            alt = fields[4]
            
            # Filter by chromosome if specified
            if chrom and vcf_chrom != chrom:
                continue
            
            # Filter by position if specified
            if pos and vcf_pos != pos:
                continue
            
            # Skip multi-allelic sites (for now, take first ALT)
            if ',' in alt:
                alt = alt.split(',')[0]
            
            # Skip insertions/deletions longer than 50bp
            if len(ref) > 50 or len(alt) > 50:
                skipped += 1
                continue
            
            variants.append({
                'chrom': vcf_chrom,
                'pos': vcf_pos,
                'id': variant_id,
                'ref': ref,
                'alt': alt
            })
    
    if skipped > 0:
        print(f"  Skipped {skipped} variants (multi-allelic or large indels)", file=sys.stderr)
    
    print(f"  Found {len(variants)} variants to process", file=sys.stderr)
    return variants

def extract_flanking_sequence(sequences, chrom, pos, ref, alt, flank_length):
    """Extract flanking sequences with variant in brackets"""
    
    if chrom not in sequences:
        print(f"Warning: Chromosome {chrom} not found in reference", file=sys.stderr)
        return None
    
    seq = sequences[chrom]
    
    # Convert to 0-based indexing
    pos_0 = pos - 1
    
    # Check if position is within chromosome bounds
    if pos_0 < 0 or pos_0 >= len(seq):
        print(f"Warning: Position {pos} out of bounds for {chrom}", file=sys.stderr)
        return None
    
    # Extract flanking sequences
    upstream_start = max(0, pos_0 - flank_length)
    upstream_seq = seq[upstream_start:pos_0]
    
    downstream_end = min(len(seq), pos_0 + len(ref) + flank_length)
    downstream_seq = seq[pos_0 + len(ref):downstream_end]
    
    # Verify reference allele matches
    ref_in_genome = seq[pos_0:pos_0 + len(ref)]
    if ref_in_genome != ref:
        print(f"Warning: Reference mismatch at {chrom}:{pos} (VCF: {ref}, Genome: {ref_in_genome})", file=sys.stderr)
        # Still proceed, but note the mismatch
    
    return {
        'upstream': upstream_seq,
        'downstream': downstream_seq,
        'ref': ref,
        'alt': alt
    }

def format_kasp_output(result, variant):
    """Format output in KASP primer format"""
    upstream = result['upstream'].lower()
    downstream = result['downstream'].lower()
    
    # Format variant as [REF/ALT]
    variant_bracket = f"[{result['ref']}/{result['alt']}]"
    
    # Create header line with variant info
    header = f">{variant['chrom']}:{variant['pos']}"
    if variant['id'] != '.':
        header += f" {variant['id']}"
    header += f" REF={result['ref']} ALT={result['alt']}"
    
    # Sequence line
    sequence = f"{upstream}{variant_bracket}{downstream}"
    
    return f"{header}\n{sequence}"

def main():
    parser = argparse.ArgumentParser(
        description='Extract flanking sequences for KASP primer design (batch mode)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process entire VCF (all chromosomes, all variants)
  python kasp_extractor_batch.py -v variants.vcf -r genome.fasta -o kasp_all.txt
  
  # Process specific chromosome only
  python kasp_extractor_batch.py -v variants.vcf -r genome.fasta -c chr1 -o kasp_chr1.txt
  
  # Process single variant
  python kasp_extractor_batch.py -v variants.vcf -r genome.fasta -c chr1 -p 12345 -o kasp_single.txt
  
  # Custom flanking length (default: 100bp)
  python kasp_extractor_batch.py -v variants.vcf -r genome.fasta -l 150 -o kasp_150bp.txt
  
Output format:
  >chr1:12345 rs123 REF=A ALT=G
  upstream_sequence[A/G]downstream_sequence
        '''
    )
    
    parser.add_argument('-v', '--vcf', required=True, 
                        help='Input VCF file')
    parser.add_argument('-r', '--reference', required=True, 
                        help='Reference genome FASTA file')
    parser.add_argument('-c', '--chrom', 
                        help='Chromosome name (optional, processes all if not specified)')
    parser.add_argument('-p', '--position', type=int, 
                        help='Variant position (optional, processes all if not specified)')
    parser.add_argument('-l', '--length', type=int, default=100, 
                        help='Flanking sequence length in bp (default: 100)')
    parser.add_argument('-o', '--output', required=True,
                        help='Output file (all results in single file)')
    parser.add_argument('--skip-indels', action='store_true',
                        help='Skip insertion/deletion variants (only process SNPs)')
    parser.add_argument('--only-indels', action='store_true',
                        help='Process only insertion/deletion variants (skip SNPs)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.position and not args.chrom:
        parser.error("--position requires --chrom to be specified")
    
    if args.skip_indels and args.only_indels:
        parser.error("--skip-indels and --only-indels cannot be used together")
    
    # Print processing mode
    print("=" * 70, file=sys.stderr)
    print("KASP EXTRACTOR - BATCH MODE", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    
    if args.chrom and args.position:
        print(f"Mode: Single variant ({args.chrom}:{args.position})", file=sys.stderr)
    elif args.chrom:
        print(f"Mode: Entire chromosome ({args.chrom})", file=sys.stderr)
    else:
        print("Mode: Entire VCF (all chromosomes)", file=sys.stderr)
    
    print(f"Flanking length: {args.length} bp", file=sys.stderr)
    print(f"Output file: {args.output}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    
    # Parse reference genome
    sequences = parse_fasta(args.reference)
    
    # Parse VCF variants
    variants = parse_vcf_variants(args.vcf, args.chrom, args.position)
    
    if not variants:
        print("Error: No variants found matching criteria", file=sys.stderr)
        sys.exit(1)
    
    # Process variants and write to output file
    print(f"\nProcessing {len(variants)} variants...", file=sys.stderr)
    
    processed = 0
    failed = 0
    skipped_indels = 0
    skipped_snps = 0
    
    with open(args.output, 'w') as out_f:
        # Write header comment
        out_f.write(f"# KASP Primer Design Sequences\n")
        out_f.write(f"# Generated from: {args.vcf}\n")
        out_f.write(f"# Reference: {args.reference}\n")
        out_f.write(f"# Flanking length: {args.length} bp\n")
        if args.chrom:
            out_f.write(f"# Chromosome filter: {args.chrom}\n")
        if args.position:
            out_f.write(f"# Position filter: {args.position}\n")
        out_f.write(f"# Total variants: {len(variants)}\n")
        out_f.write("#\n")
        out_f.write("# Format: >chr:pos [id] REF=X ALT=Y\n")
        out_f.write("#         upstream_sequence[REF/ALT]downstream_sequence\n")
        out_f.write("#\n\n")
        
        for i, variant in enumerate(variants, 1):
            # Progress update every 1000 variants
            if i % 1000 == 0:
                print(f"  Processed {i:,} / {len(variants):,} variants...", file=sys.stderr)
            
            # Skip indels if requested
            if args.skip_indels:
                if len(variant['ref']) > 1 or len(variant['alt']) > 1:
                    skipped_indels += 1
                    continue
            
            # Process only indels if requested
            if args.only_indels:
                if len(variant['ref']) == 1 and len(variant['alt']) == 1:
                    skipped_snps += 1
                    continue
            
            # Extract flanking sequences
            result = extract_flanking_sequence(
                sequences,
                variant['chrom'],
                variant['pos'],
                variant['ref'],
                variant['alt'],
                args.length
            )
            
            if not result:
                failed += 1
                continue
            
            # Format and write output
            output = format_kasp_output(result, variant)
            out_f.write(output + "\n\n")
            processed += 1
    
    # Print summary
    print("\n" + "=" * 70, file=sys.stderr)
    print("PROCESSING COMPLETE", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"Total variants in VCF: {len(variants)}", file=sys.stderr)
    print(f"Successfully processed: {processed}", file=sys.stderr)
    if skipped_indels > 0:
        print(f"Skipped indels: {skipped_indels}", file=sys.stderr)
    if skipped_snps > 0:
        print(f"Skipped SNPs: {skipped_snps}", file=sys.stderr)
    if failed > 0:
        print(f"Failed: {failed}", file=sys.stderr)
    print(f"\nOutput written to: {args.output}", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

if __name__ == '__main__':
    main()
