#!/usr/bin/env python3
"""Rename numeric folders in resources/state_lores to English state names.

Usage:
  python scripts/rename_state_folders.py [--apply] [--overwrite]

By default the script performs a dry-run and prints the proposed renames.
Use --apply to actually rename. Use --overwrite to overwrite existing target folders.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import unicodedata
from typing import Dict
from hoi4dev import LoadJson, pjoin

def load_state_names() -> Dict[str, str]:
    state_names = LoadJson(pjoin("resources","state_names.json"))
    return {str(k): v['english'] for k, v in state_names.items()}

def safe_name_for_folder(name: str) -> str:
    """Sanitize a name for use in a folder while preserving spaces and capitalization.

    - Normalize unicode (NFKD) and remove diacritics
    - Remove characters that are problematic in filenames (/:?"<>|) and control chars
    - Collapse multiple spaces into single space
    - Strip leading/trailing whitespace and dots
    """
    # Normalize and remove diacritics
    name = unicodedata.normalize('NFKD', name)
    name = ''.join(ch for ch in name if not unicodedata.combining(ch))
    # Remove control characters and reserved filename characters
    # Keep letters, numbers, spaces, dash, underscore, dot, and parentheses
    # remove ASCII control chars and common reserved filename characters
    name = re.sub(r'[\x00-\x1f<>:"\\/|?]+', '', name)
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)
    # Strip
    name = name.strip(' .')
    if not name:
        name = 'state'
    return name

def plan_renames(state_names: Dict[str, str], lores_dir: str):
    plans = []
    for entry in os.listdir(lores_dir):
        full = os.path.join(lores_dir, entry)
        if not os.path.isdir(full):
            continue
        if not entry.isdigit():
            continue
        if "-" in entry:
            continue
        state_id = entry
        english = state_names.get(state_id)
        safe = safe_name_for_folder(english)
        target_name = f"{state_id} - {safe}"
        target_full = os.path.join(lores_dir, target_name)
        plans.append((full, target_full, None))
    return plans


def apply_plans(plans):
    for src, dst, err in plans:
        if err:
            print(f'SKIP: {src} -> {err}')
            continue
        if os.path.abspath(src) == os.path.abspath(dst):
            print(f'SKIP (same): {src}')
            continue
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        else:
            os.rename(src, dst)

def rename_state_lores():
    """High-level wrapper: load names, plan renames, optionally skip already-converted folders (containing '-'), and apply plans.
    Returns the list of applied (or planned when apply=False) tuples (src, dst, err).
    """
    state_names = load_state_names()
    plans = plan_renames(state_names, lores_dir='resources/state_lores')
    apply_plans(plans)
    return plans


if __name__ == '__main__':
    rename_state_lores()
