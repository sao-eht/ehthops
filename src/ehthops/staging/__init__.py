"""
Staging module for EHT HOPS pipeline.

This module handles the initial setup and data staging for the pipeline.
"""

from ehthops.staging.launch import launch_stage, setup_environment
from ehthops.staging.link import link_hops_directories

__all__ = ['launch_stage', 'setup_environment', 'link_hops_directories']
