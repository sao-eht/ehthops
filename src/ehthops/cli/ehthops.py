#!/usr/bin/env python3
"""
EHT HOPS Pipeline - Command Line Interface

A Python implementation of the EHT HOPS data processing pipeline.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union

from ehthops.logging import setup_logging
from ehthops.staging import launch_stage, link_hops_directories
from ehthops.config import load_config, validate_config, get_base_dir, get_stage_name, get_stage_map


def run_pipeline(config: Dict[str, Any], logger: logging.Logger, base_dir: Optional[Union[str, Path]] = None) -> None:
    """
    Run the EHT-HOPS pipeline.
    
    Args:
        config: Configuration dictionary from YAML
        logger: Logger instance
        base_dir: Base directory for pipeline outputs.
                 If not specified, must be provided via config or will error.
    """
    logger.info("Starting EHT-HOPS Pipeline")

    # Display configuration summary
    logger.info(f"Source directory: {config['data']['srcdir']}")
    logger.info(f"Filter subdirectories in order: {config['data']['corrdat']}")
    logger.info(f"Campaign: {config['observation']['campaign']}")
    logger.info(f"Year: {config['observation']['year']}")
    logger.info(f"Band: {config['data']['band']}")
    
    stages = config['pipeline']['stages']
    logger.info(f"Pipeline stages to run: {len(stages)} stages")
    
    base_dir = get_base_dir(config, base_dir)
    logger.info(f"Using base directory: {base_dir}")
    
    if not base_dir.exists():
        logger.info(f"Creating base directory: {base_dir}")
        base_dir.mkdir(parents=True, exist_ok=True)
    
    for i, stage in enumerate(stages, start=1):
        stage_name = get_stage_name(stage)
        logger.info(f"Stage {i}/{len(stages)}: {stage} ({stage_name})")
        
        try:
            env = launch_stage(config, stage, base_dir)
        except Exception as e:
            logger.error(f"Failed to launch stage {stage} ({stage_name}): {e}")
            raise
        
        logger.info(f"  Processing stage {stage} ({stage_name})...")
        
        # Run linking step for stages 0-5 (before uvfits conversion)
        if stage <= 5:
            try:
                logger.info(f"Linking MK4 data from {config['data']['srcdir']} to {base_dir/stage_name}/")
                link_hops_directories(env)
            except RuntimeError as e:
                logger.error(f"Linking failed: {e}")
                raise
        
        # TODO: Implement stage-specific processing
        # This is where you would call the appropriate processing functions
        # for each stage based on the stage name
        
        if stage == 0: pass            
        elif stage == 1: pass
        elif stage == 2: pass
        elif stage == 3: pass
        elif stage == 4: pass
        elif stage == 5: pass
        elif stage == 6: pass
        elif stage == 7: pass
        elif stage == 8: pass
        
        logger.info(f"  Stage {stage} ({stage_name}) completed")
    
    logger.info("Pipeline execution completed successfully")


def main() -> None:
    """Main entry point for the EHT-HOPS pipeline."""
    
    # Get stage mapping for help text
    STAGE_MAP = get_stage_map()
    
    stage_help = "Valid stages:\n"
    for num, name in STAGE_MAP.items():
        stage_help += f"  {num}: {name}\n"
    
    parser = argparse.ArgumentParser(
        description="EHT-HOPS Data Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{stage_help}
Examples:
  %(prog)s settings.yaml --base-dir /path/to/outputs
  %(prog)s -v settings.yaml --base-dir ~/eht/run1
  %(prog)s --dry-run settings.yaml --base-dir ./outputs
  %(prog)s settings.yaml --stages 0 1 2
  
  # Or specify base_dir in settings.yaml under pipeline section
  %(prog)s settings.yaml
        """
    )
    
    parser.add_argument(
        'config',
        help='Path to the YAML configuration file (e.g., settings.yaml)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging output'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually running the pipeline'
    )
    
    parser.add_argument(
        '--stages',
        nargs='+',
        type=int,
        choices=range(0, 9),
        metavar='STAGE',
        help='Run only specific stages (integers 0-8, e.g., --stages 0 1 2)'
    )
    
    parser.add_argument(
        '--base-dir',
        help='Base directory for pipeline outputs. Stage directories will be created here. '
             'Can also be specified in settings.yaml under pipeline.base_dir'
    )
    
    args = parser.parse_args()
    
    logger = setup_logging(args.verbose)
    
    config = load_config(args.config)
    
    if not validate_config(config):
        sys.exit(1)
    
    # Override stages if specified
    if args.stages:
        logger.info(f"Overriding stages with: {args.stages}")
        config['pipeline']['stages'] = args.stages
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No actual processing will be performed")
        logger.info("Configuration loaded successfully:")
        logger.info(f"  Config file: {args.config}")
        logger.info(f"  Source dir: {config['data']['srcdir']}")
        
        # Display stages with their names
        stage_info = []
        for stage_num in config['pipeline']['stages']:
            stage_name = get_stage_name(stage_num)
            stage_info.append(f"{stage_num} ({stage_name})")
        logger.info(f"  Stages: {', '.join(stage_info)}")
        
        if args.base_dir:
            logger.info(f"  Base dir: {args.base_dir}")
        logger.info("Pipeline would execute the above configuration.")
    else:
        try:
            run_pipeline(config, logger, base_dir=args.base_dir)
        except KeyboardInterrupt:
            logger.warning("Pipeline interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exception()
            sys.exit(1)


if __name__ == "__main__":
    main()