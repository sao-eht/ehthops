"""
Link module for EHT HOPS pipeline.

This module handles linking HOPS directories from source to working directory.
Replicates the functionality of the bash 2.link script.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


def should_skip_file(file_path: Path, band: str, haxp: bool = False) -> bool:
    """
    Determine if a file should be skipped based on filtering criteria.
    
    Args:
        file_path: Path to the file to check
        band: Band identifier (e.g., 'b1', 'b2', etc.)
        haxp: Whether we're currently processing HAXP data
        
    Returns:
        True if file should be skipped, False otherwise
    """
    file_str = str(file_path)
    
    # Skip files in haxp directories when not processing HAXP
    if not haxp and 'haxp' in file_str.lower():
        return True
    
    # Skip files that don't contain the requested band
    if f'-{band}-' not in file_str:
        return True
    
    return False


def is_valid_root_filename(filename: str) -> bool:
    """
    Check if filename matches HOPS root file pattern.
    
    Pattern: ^[a-zA-Z0-9+_-]+\.[a-zA-Z0-9]{6}$
    
    Args:
        filename: Filename to check
        
    Returns:
        True if filename matches pattern, False otherwise
    """
    pattern = r'^[a-zA-Z0-9+_-]+\.[a-zA-Z0-9]{6}$'
    return re.match(pattern, filename) is not None


def is_valid_expt_no(dirname: str) -> bool:
    """
    Check if directory name is a valid experiment number.
    
    Pattern: ^[0-9]{4,5}$
    
    Args:
        dirname: Directory name to check
        
    Returns:
        True if valid experiment number, False otherwise
    """
    pattern = r'^[0-9]{4,5}$'
    return re.match(pattern, dirname) is not None


def extract_extension(filename: str) -> str:
    """
    Extract the 6-character extension from a root filename.
    
    Args:
        filename: Root filename
        
    Returns:
        6-character extension
    """
    match = re.search(r'[a-zA-Z0-9]{6}$', filename)
    if match:
        return match.group(0)
    return ""


def get_max_extension(scan_dir: Path) -> str:
    """
    Get the maximum (lexicographically) extension in a scan directory.
    
    Args:
        scan_dir: Path to scan directory
        
    Returns:
        Maximum extension found, or empty string if none found
    """
    extensions: Set[str] = set()
    
    if not scan_dir.exists():
        return ""
    
    for file_path in scan_dir.rglob('*'):
        if file_path.is_file():
            ext = extract_extension(file_path.name)
            if ext:
                extensions.add(ext)
    
    if extensions:
        return max(extensions)
    return ""


def find_root_files(srcdir: Path, corrdat: List[str], band: str) -> List[Path]:
    """
    Find all valid root files in source directories.
    
    Args:
        srcdir: Source directory path
        corrdat: List of correlation data directories
        band: Band identifier
        
    Returns:
        List of paths to valid root files
    """
    root_files = []
    
    for d in corrdat:
        search_path = srcdir / d
        if not search_path.exists():
            logger.warning(f"Source directory does not exist: {search_path}")
            continue
        
        logger.debug(f"Searching for root files in: {search_path}")
        
        # Find all files recursively
        for file_path in search_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            # Check if filename matches root file pattern
            if not is_valid_root_filename(file_path.name):
                continue
            
            # Apply filtering
            if should_skip_file(file_path, band):
                continue
            
            root_files.append(file_path)
    
    return root_files


def link_scan_files(src_scan_dir: Path, dest_scan_dir: Path, extension: str) -> int:
    """
    Create symbolic links for all files in a scan directory with matching extension.
    
    Args:
        src_scan_dir: Source scan directory
        dest_scan_dir: Destination scan directory
        extension: 6-character extension to match
        
    Returns:
        Number of files linked
    """
    linked_count = 0
    
    # Pattern to exclude calibration files (e.g., AA.X.1.abc123)
    exclude_pattern = re.compile(r'[A-Za-z]{2}\.[A-Za-z]\.[0-9]+\.[A-Za-z0-9]{6}$')
    
    for file_path in src_scan_dir.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Check if file has the matching extension
        if not file_path.name.endswith(f'.{extension}'):
            continue
        
        # Skip calibration files
        if exclude_pattern.search(file_path.name):
            continue
        
        # Create symbolic link
        dest_file = dest_scan_dir / file_path.name
        try:
            dest_file.symlink_to(file_path)
            linked_count += 1
            logger.debug(f"Linked: {file_path} -> {dest_file}")
        except FileExistsError:
            logger.debug(f"Link already exists: {dest_file}")
        except Exception as e:
            logger.error(f"Failed to link {file_path}: {e}")
    
    return linked_count


def process_haxp_data(src_scan_dir: Path, dest_scan_dir: Path) -> int:
    """
    Replace ALMA data with HAXP data if available.
    
    Args:
        src_scan_dir: Source scan directory (hops)
        dest_scan_dir: Destination scan directory
        
    Returns:
        Number of HAXP files linked
    """
    # Generate haxp directory by replacing "hops" with "haxp"
    haxp_scan_dir = Path(str(src_scan_dir).replace('/hops/', '/haxp/'))
    
    if not haxp_scan_dir.exists():
        logger.debug(f"HAXP directory does not exist: {haxp_scan_dir}")
        return 0
    
    # Remove all ALMA files (starting with "A") in dest scan dir
    alma_removed = 0
    for file_path in dest_scan_dir.glob('A*'):
        try:
            file_path.unlink()
            alma_removed += 1
            logger.debug(f"Removed ALMA file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to remove ALMA file {file_path}: {e}")
    
    if alma_removed > 0:
        logger.info(f"Removed {alma_removed} ALMA files for HAXP replacement")
    
    # Link HAXP files
    linked_count = 0
    exclude_pattern = re.compile(r'[A-Za-z]{2}\.[A-Za-z]\.[0-9]+\.[A-Za-z0-9]{6}$')
    
    for file_path in haxp_scan_dir.rglob('*'):
        if not file_path.is_file():
            continue
        
        # Skip calibration files
        if exclude_pattern.search(file_path.name):
            continue
        
        # Create symbolic link
        dest_file = dest_scan_dir / file_path.name
        try:
            dest_file.symlink_to(file_path)
            linked_count += 1
            logger.debug(f"Linked HAXP: {file_path} -> {dest_file}")
        except FileExistsError:
            logger.debug(f"HAXP link already exists: {dest_file}")
        except Exception as e:
            logger.error(f"Failed to link HAXP file {file_path}: {e}")
    
    logger.info(f"Linked {linked_count} HAXP files")
    return linked_count


def rename_silly_root_files(datadir: Path) -> int:
    """
    Rename root files with '_3' suffix to standard names.
    
    Args:
        datadir: Data directory path
        
    Returns:
        Number of files renamed
    """
    renamed_count = 0
    
    for file_path in datadir.rglob('*_3*'):
        if not file_path.is_file():
            continue
        
        # Generate new name by removing '_3'
        new_name = file_path.name.replace('_3', '')
        new_path = file_path.parent / new_name
        
        try:
            file_path.rename(new_path)
            renamed_count += 1
            logger.info(f"Renamed: {file_path.name} -> {new_name}")
        except Exception as e:
            logger.error(f"Failed to rename {file_path}: {e}")
    
    return renamed_count


def link_hops_directories(env: Dict[str, str]) -> None:
    """
    Link HOPS directories from source to working directory.
    
    This is the main function that replicates the bash 2.link script.
    
    Args:
        env: Environment dictionary containing:
            - WRKDIR: Working directory
            - SRCDIR: Source directory
            - METADIR: Metadata directory
            - CORRDAT: Correlation data (list or comma-separated string)
            - DATADIR: Data output directory
            - BAND: Band identifier
            - MIXEDPOL: Mixed polarization flag
            - HAXP: Use HAXP data flag
            
    Raises:
        RuntimeError: If no data found for the specified band
    """
    logger.info("1. Linking HOPS directories")
    
    # Extract and log environment variables
    wrkdir = Path(env['WRKDIR'])
    srcdir = Path(env['SRCDIR'])
    metadir = env['METADIR']
    corrdat_str = env['CORRDAT']
    datadir = Path(env['DATADIR'])
    band = env['BAND']
    mixedpol = env['MIXEDPOL'].lower() == 'true'
    haxp = env['HAXP'].lower() == 'true'
    
    logger.info(f"  Container work directory, WRKDIR: \"{wrkdir}\"")
    logger.info(f"  Container data source, SRCDIR:    \"{srcdir}\"")
    logger.info(f"  Metadata directory, METADIR:      \"{metadir}\"")
    logger.info(f"  Container Corr release(s), CORRDAT: \"{corrdat_str}\"")
    logger.info(f"  Container HOPS data output, DATADIR: \"{datadir}\"")
    logger.info(f"  Band, BAND:        {band}")
    logger.info(f"  Mixed pol calibration, MIXEDPOL:  {mixedpol}")
    logger.info(f"  Use HAXP data for ALMA, HAXP:     {haxp}")
    
    # Change to working directory
    os.chdir(wrkdir)
    
    # Create necessary directories
    datadir.mkdir(parents=True, exist_ok=True)
    (wrkdir / 'tests').mkdir(exist_ok=True)
    (wrkdir / 'temp').mkdir(exist_ok=True)
    (wrkdir / 'log').mkdir(exist_ok=True)
    
    # Parse corrdat (could be a list or comma/space-separated string)
    if isinstance(corrdat_str, list):
        corrdat = corrdat_str
    else:
        # Split by space, tab, newline, colon, or comma
        corrdat = re.split(r'[ \t\n:,]+', corrdat_str.strip())
        corrdat = [d.strip() for d in corrdat if d.strip()]
    
    logger.info(f"Processing {len(corrdat)} correlation data directories")
    
    # Find all root files
    root_files = find_root_files(srcdir, corrdat, band)
    logger.info(f"Found {len(root_files)} root files")
    
    # Track previous source scan directory for duplicate detection
    prev_src_scan_dir = None
    total_linked = 0
    
    # Process each root file
    for root_file in sorted(root_files):
        logger.debug(f"Processing: {root_file}")
        
        # Get parent (scan) and grandparent (expt_no) directories
        src_scan_dir = root_file.parent
        src_expt_dir = src_scan_dir.parent
        
        # Validate experiment number
        if not is_valid_expt_no(src_expt_dir.name):
            logger.debug(f"Skipping {src_expt_dir} with {root_file} (invalid expt_no)")
            continue
        
        # Create destination directory structure
        dest_expt_dir = datadir / src_expt_dir.name
        dest_scan_dir = dest_expt_dir / src_scan_dir.name
        
        # Extract extension from current root file
        extension = extract_extension(root_file.name)
        if not extension:
            logger.warning(f"Could not extract extension from: {root_file.name}")
            continue
        
        # Handle duplicate extensions
        if dest_scan_dir.exists():
            # Only check for duplicates if same source scan directory
            if src_scan_dir == prev_src_scan_dir:
                max_dest_extension = get_max_extension(dest_scan_dir)
                
                if max_dest_extension:
                    # Compare extensions lexicographically
                    if extension <= max_dest_extension:
                        logger.info(f"Skipping {extension} in favour of {max_dest_extension}")
                        prev_src_scan_dir = src_scan_dir
                        continue
                    else:
                        logger.info(f"Replacing {max_dest_extension} with extension {extension}")
                        # Remove old scan directory
                        import shutil
                        shutil.rmtree(dest_scan_dir)
            else:
                # Different scan directory, skip this iteration
                prev_src_scan_dir = src_scan_dir
                continue
        
        # Create destination scan directory
        dest_scan_dir.mkdir(parents=True, exist_ok=True)
        
        # Link scan files with matching extension
        linked = link_scan_files(src_scan_dir, dest_scan_dir, extension)
        total_linked += linked
        
        # Update previous scan directory
        prev_src_scan_dir = src_scan_dir
        
        # Process HAXP data if enabled
        if haxp:
            haxp_linked = process_haxp_data(src_scan_dir, dest_scan_dir)
            total_linked += haxp_linked
    
    logger.info(f"Total files linked: {total_linked}")
    
    # Rename silly root files
    renamed = rename_silly_root_files(datadir)
    if renamed > 0:
        logger.info(f"Renamed {renamed} files with '_3' suffix")
    
    # Verify that data was found
    expt_dirs = [d for d in datadir.iterdir() if d.is_dir() and re.match(r'^[0-9]{4,5}$', d.name)]
    
    if not expt_dirs:
        error_msg = (
            f"ERROR: No data in the archive to link for band {band}!\n"
            f"       SRCDIR={srcdir}\n"
            f"       CORRDAT={corrdat}\n"
            f"       Ensure that the above paths exist and the string '-{band}-' "
            f"exists somewhere along the path to the data archive."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    logger.info(f"Successfully linked data for {len(expt_dirs)} experiments")
