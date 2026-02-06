"""
Launch module for EHT HOPS pipeline.

This module handles the setup and initialization of the pipeline environment,
replicating the functionality of the bash 0.launch script.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Union
from ehthops.logging import get_logger

logger = get_logger(__name__)


def validate_directories(env: Dict[str, str]) -> None:
    """
    Validate that required directories exist.
    
    Args:
        env: Environment dictionary
        
    Raises:
        SystemExit: If required directories don't exist
    """
    metadir = Path(env['METADIR'])
    srcdir = Path(env['SRCDIR'])
    
    if not metadir.exists():
        logger.error(f"METADIR={metadir} does not exist! Exiting...")
        sys.exit(1)
    else:
        logger.debug(f"METADIR={metadir} exists")
    
    if not srcdir.exists():
        logger.error(f"SRCDIR={srcdir} does not exist! Exiting...")
        sys.exit(1)
    else:
        logger.debug(f"SRCDIR={srcdir} exists")


def log_environment(env: Dict[str, str]) -> None:
    """
    Log environment configuration.
    
    Args:
        env: Environment dictionary
    """
    logger.info("Pipeline environment configuration:")
    logger.info(f"  Corr release(s), CORRDAT:   {env['CORRDAT']}")
    logger.info(f"  Data source dir, SRCDIR:    {env['SRCDIR']}")
    logger.info(f"  Work dir, WRKDIR:           {env['WRKDIR']}")
    logger.info(f"  Top level work dir, TOPDIR: {env['TOPDIR']}")
    logger.info(f"  HOPS data output, DATADIR:  {env['DATADIR']}")
    logger.info(f"  Meta, METADIR:              {env['METADIR']}")
    logger.info(f"  Band, BAND:                 {env['BAND']}")
    logger.info(f"  Pattern, PATTERN:           {env.get('PATTERN', '')}")
    logger.info(f"  Campaign year, OBSYEAR:     {env['OBSYEAR']}")
    logger.info(f"  Mixed pol cal, MIXEDPOL:    {env['MIXEDPOL']}")
    logger.info(f"  Use HAXP data, HAXP:        {env['HAXP']}")


def copy_control_files(env: Dict[str, str], stage_dir: Path) -> None:
    """
    Copy stage-specific control files from METADIR.
    
    Replicates the bash script's control file copying logic:
    - Extracts stage number from directory name (e.g., "0.bootstrap" -> "0")
    - Copies cf files matching patterns: cf<N>_bx_* and cf<N>_<band>_*
    
    Args:
        env: Environment dictionary
        stage_dir: Path to the current stage directory
    """
    import shutil
    import glob
    
    # Get stage number from directory name
    stage_name = stage_dir.name
    stage_num = stage_name.split('.')[0] if '.' in stage_name else '0'
    
    # Determine target directory (parent of bin/ where we are)
    ndir = stage_dir
    
    # Patterns for control files
    metadir = Path(env['METADIR'])
    cf_dir = metadir / 'cf'
    
    if not cf_dir.exists():
        logger.warning(f"Control file directory {cf_dir} does not exist, skipping control file copy")
        return
    
    band = env['BAND']
    pattern1 = f"cf{stage_num}_bx_*"
    pattern2 = f"cf{stage_num}_{band}_*"
    
    logger.info(f"Copying control files from {cf_dir} to {ndir}")
    logger.debug(f"  Patterns: {pattern1}, {pattern2}")
    
    # Find and copy matching files
    files_copied = 0
    for pattern in [pattern1, pattern2]:
        for src_file in cf_dir.glob(pattern):
            dest_file = ndir / src_file.name
            # Only copy if destination doesn't exist (cp -n behavior)
            if not dest_file.exists():
                shutil.copy2(src_file, dest_file)
                logger.debug(f"  Copied: {src_file.name}")
                files_copied += 1
            else:
                logger.debug(f"  Skipped (exists): {src_file.name}")
    
    if files_copied > 0:
        logger.info(f"  Copied {files_copied} control file(s)")
    else:
        logger.info("  No new control files to copy")


def setup_environment(config: Dict[str, Any], stage_dir: Path) -> Dict[str, str]:
    """
    Setup environment for a pipeline stage.
    
    This replicates the functionality of the bash 0.launch script, setting up
    directories and environment variables for HOPS processing.
    
    Args:
        config: Configuration dictionary loaded from YAML
        stage_dir: Path to the current stage directory
        
    Returns:
        Environment dictionary with all necessary paths and settings
    """
    logger.info("Setting up pipeline environment")
    
    # Extract configuration values
    srcdir = config['data']['srcdir']
    corrdat = config['data']['corrdat']
    metadir = config['data']['metadir']
    band = config['data'].get('band', 'b1')  # Get band from config with default
    pattern = config['data'].get('pattern', '')  # Get pattern from config
    obsyear = config['observation']['year']
    mixedpol = config['polarization']['mixedpol']
    haxp = config['polarization']['haxp']
    
    # Set up directory paths (similar to bash script)
    wrkdir = stage_dir.resolve()
    topdir = wrkdir.parent
    datadir = wrkdir / 'data'
    
    # Create environment dictionary
    env = {
        'CORRDAT': corrdat,
        'WRKDIR': str(wrkdir),
        'TOPDIR': str(topdir),
        'DATADIR': str(datadir),
        'SRCDIR': srcdir,
        'METADIR': metadir,
        'BAND': band,
        'PATTERN': pattern,
        'OBSYEAR': obsyear,
        'MIXEDPOL': str(mixedpol).lower(),
        'HAXP': str(haxp).lower(),
    }

    # If HAXP=true and MIXEDPOL=false, set MIXEDPOL=true
    if haxp and not mixedpol:
        env['MIXEDPOL'] = 'true'
        logger.warning("MIXEDPOL set to true because HAXP is set to true")
    
    # Validate directories
    validate_directories(env)
    
    # Log the environment setup
    log_environment(env)
    
    # Copy control files from metadata directory to stage directory
    copy_control_files(env, stage_dir)
    
    return env


def launch_stage(config: Dict[str, Any], stage_num: int, base_dir: Union[str, Path]) -> Dict[str, str]:
    """
    Launch a specific pipeline stage.
    
    Args:
        config: Configuration dictionary from YAML
        stage_num: Stage number (0-8)
        base_dir: Base directory for pipeline outputs.
                 Stage directories will be created here.
    
    Returns:
        Environment dictionary for the stage
    """
    base_dir = Path(base_dir)
    
    # Get the stage directory name from the stage number
    from ehthops.config import get_stage_name
    stage_name = get_stage_name(stage_num)
    
    stage_dir = base_dir / stage_name
    
    # Create stage directory if it doesn't exist
    if not stage_dir.exists():
        logger.info(f"Creating stage directory: {stage_dir}")
        stage_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Launching stage {stage_num}: {stage_name}")
    
    env = setup_environment(config, stage_dir)
    
    return env
