"""
Configuration management for EHT HOPS pipeline.

This module handles loading, validation, and management of pipeline configuration.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union


# Stage number to directory name mapping
# This is the authoritative mapping for all pipeline stages
STAGE_MAP: Dict[int, str] = {
    0: "0.bootstrap",
    1: "1.+flags+wins",
    2: "2.+pcal",
    3: "3.+adhoc",
    4: "4.+delays",
    5: "5.+close",
    6: "6.uvfits",
    7: "7.+apriori",
    8: "8.+polcal"
}


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        SystemExit: If file not found or invalid YAML
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in configuration file: {e}")
        sys.exit(1)


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate required configuration parameters.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_sections = ['data', 'pipeline', 'observation']
    
    for section in required_sections:
        if section not in config:
            print(f"Error: Missing required section '{section}' in configuration.")
            return False
    
    # Check required data fields
    if 'srcdir' not in config['data']:
        print("Error: Missing 'srcdir' in data configuration.")
        return False
    
    if 'band' not in config['data']:
        print("Error: Missing 'band' in data configuration.")
        return False
    
    if 'stages' not in config['pipeline']:
        print("Error: Missing 'stages' in pipeline configuration.")
        return False
    
    # Validate that all stages are valid integers
    for stage_num in config['pipeline']['stages']:
        if not isinstance(stage_num, int):
            print(f"Error: Stage '{stage_num}' must be an integer (0-8).")
            return False
        if stage_num not in STAGE_MAP:
            print(f"Error: Invalid stage number '{stage_num}'. Valid stages: {list(STAGE_MAP.keys())}")
            return False
    
    return True


def get_base_dir(config: Dict[str, Any], base_dir_arg: Optional[Union[str, Path]] = None) -> Path:
    """
    Determine the base directory for pipeline outputs.
    
    Priority:
    1. Command line argument (base_dir_arg)
    2. Configuration file (config['pipeline']['base_dir'])
    3. Error if neither specified
    
    Args:
        config: Configuration dictionary
        base_dir_arg: Base directory from command line
        
    Returns:
        Base directory path
        
    Raises:
        SystemExit: If no base directory specified
    """
    if base_dir_arg is not None:
        return Path(base_dir_arg)
    
    if 'base_dir' in config['pipeline'] and config['pipeline']['base_dir']:
        return Path(config['pipeline']['base_dir'])
    
    print("Error: No base directory specified.")
    print("  Use --base-dir argument or set 'base_dir' in config under 'pipeline' section.")
    sys.exit(1)


def get_stage_name(stage_num: int) -> str:
    """
    Get the directory name for a stage number.
    
    Args:
        stage_num: Stage number (0-8)
        
    Returns:
        Stage directory name (e.g., "0.bootstrap", "1.+flags+wins")
        
    Raises:
        KeyError: If stage number is not in the stage map
    """
    if stage_num not in STAGE_MAP:
        raise KeyError(f"Invalid stage number {stage_num}. Valid stages: {list(STAGE_MAP.keys())}")
    return STAGE_MAP[stage_num]


def get_stage_map() -> Dict[int, str]:
    """
    Get the stage mapping.
    
    Returns:
        Dictionary mapping stage numbers to directory names
    """
    return STAGE_MAP.copy()
