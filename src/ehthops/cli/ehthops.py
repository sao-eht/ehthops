#!/usr/bin/env python3
"""
EHT HOPS Pipeline - Command Line Interface

A Python implementation of the EHT HOPS data processing pipeline.
"""

import argparse
import sys
import yaml
from pathlib import Path

from ehthops.logging import setup_logging


def load_config(config_path):
    """Load configuration from YAML file."""
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


def validate_config(config):
    """Validate required configuration parameters."""
    required_sections = ['data', 'pipeline', 'observation']
    
    for section in required_sections:
        if section not in config:
            print(f"Error: Missing required section '{section}' in configuration.")
            return False
    
    # Check required data fields
    if 'srcdir' not in config['data']:
        print("Error: Missing 'srcdir' in data configuration.")
        return False
    
    if 'stages' not in config['pipeline']:
        print("Error: Missing 'stages' in pipeline configuration.")
        return False
    
    return True


def run_pipeline(config, logger):
    """Run the EHT HOPS pipeline."""
    logger.info("Starting EHT HOPS Pipeline")
    
    # Display configuration summary
    logger.info(f"Source directory: {config['data']['srcdir']}")
    logger.info(f"Correlation data: {config['data']['corrdat']}")
    logger.info(f"Campaign: {config['observation']['campaign']}")
    logger.info(f"Year: {config['observation']['year']}")
    
    stages = config['pipeline']['stages']
    logger.info(f"Pipeline stages to run: {len(stages)} stages")
    
    for i, stage in enumerate(stages):
        logger.info(f"Stage {i}/{len(stages)}: {stage}")
        
        # TODO: Implement actual stage processing
        # This is where you would call the appropriate processing functions
        # For now, just simulate the stage execution
        logger.info(f"  Processing stage {stage}...")
        
        # Example of what each stage might do:
        if stage == "0.bootstrap":
            logger.info("  - Setting up data directories")
            logger.info("  - Validating input data")
        elif stage == "1.+flags+wins":
            logger.info("  - Applying flags")
            logger.info("  - Setting time windows")
        elif stage == "2.+pcal":
            logger.info("  - Running phase calibration")
        # ... etc for other stages
        
        logger.info(f"  Stage {stage} completed")
    
    logger.info("Pipeline execution completed successfully")


def main():
    """Main entry point for the EHT HOPS pipeline."""
    parser = argparse.ArgumentParser(
        description="EHT HOPS Data Processing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s settings.yaml
  %(prog)s -v /path/to/custom/settings.yaml
  %(prog)s --dry-run settings.yaml
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
        help='Run only specific stages (e.g., --stages "0.bootstrap" "1.+flags+wins")'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Load and validate configuration
    config = load_config(args.config)
    
    if not validate_config(config):
        sys.exit(1)
    
    # Override stages if specified
    if args.stages:
        logger.info(f"Overriding stages with: {args.stages}")
        config['pipeline']['stages'] = args.stages
    
    # Run pipeline or show dry-run
    if args.dry_run:
        logger.info("DRY RUN MODE - No actual processing will be performed")
        logger.info("Configuration loaded successfully:")
        logger.info(f"  Config file: {args.config}")
        logger.info(f"  Source dir: {config['data']['srcdir']}")
        logger.info(f"  Stages: {config['pipeline']['stages']}")
        logger.info("Pipeline would execute the above configuration.")
    else:
        try:
            run_pipeline(config, logger)
        except KeyboardInterrupt:
            logger.warning("Pipeline interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()