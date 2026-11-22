#!/usr/bin/env python3
"""Descriptive accounting of the frozen Tampa exact-point return-fragility summary.

No biological-response fitting, threshold search, prospective validation or
independence assumption is performed. Observations are four-year sequences.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = Path('results/return_fragility_v1.json')


def derive(source: dict) -> dict:
    if source.get('schema') != 'tampa.return_fragility_v1.canonical_summary':
        raise ValueError('Unexpected canonical summary schema')
    if source.get('status') != 'return_fragility_supported':
        raise ValueError('Unexpected original result status')
    r = source['registry']
    s = source['secondary']
    total, re, co, events = [int(r[k]) for k in (
        'four_year_sequences', 'recovered_sequences',
        'continuous_sequences', 'total_recorded_relosses'
    )]
    if min(total, re, co, events) < 1 or re + co != total or events > total:
        raise ValueError('Registry counts inconsistent')
    p_re = float(s['recovered_reloss_fraction'])
    p_co = float(s['continuous_reloss_fraction'])
    if not all(math.isfinite(p) and 0 <= p <= 1 for p in (p_re, p_co)):
        raise ValueError('Invalid probabilities')
    re_events = round(re * p_re)
    co_events = round(co * p_co)
    if (not math.isclose(re_events / re, p_re, rel_tol=0, abs_tol=1e-12)
            or not math.isclose(co_events / co, p_co, rel_tol=0, abs_tol=1e-12)
            or re_events + co_events != events):
        raise ValueError('Loss fractions/counts do not agree with canonical source')
    if p_co == 0:
        raise ValueError('Undefined relative risk when control rate is zero')
    fraction_flagged = re / total
    fraction_events = re_events / events
    return {
        'schema': 'tampa.return_history_monitoring_arithmetic_v1',
        'evidence_class': 'posthoc_descriptive_reaggregation_of_existing_result',
        'source_result': str(SOURCE),
        'unit': 'overlapping eligible four_year_exact_point_sequences_not_independent_sites',
        'denominators': {
            'all_sequences': total,
            're_recorded_sequences': re,
            'uninterrupted_sequences': co,
            'all_next_year_recorded_non_detections': events,
            're_recorded_next_year_non_detections': re_events,
            'uninterrupted_next_year_non_detections': co_events,
        },
        'descriptive': {
            're_recorded_non_detection_rate': p_re,
            'uninterrupted_non_detection_rate': p_co,
            'absolute_risk_difference_percentage_points': 100 * (p_re - p_co),
            'relative_risk': p_re / p_co,
            're_recorded_sequence_fraction': fraction_flagged,
            're_recorded_share_of_non_detections': fraction_events,
            'event_concentration_ratio': fraction_events / fraction_flagged,
        },
        'explicit_limitations': [
            'Not an independent forecast or fitted intervention effect.',
            'Sequences overlap and are clustered by exact mark and stable node.',
            'Eligibility requires repeated annual sampling and conditions on four-year completeness.',
            'Re-recording/non-detection is not demographic recovery/mortality.',
            'Shares and concentration compare observed past outcomes, not a predeclared operational watchlist.',
            'No new uncertainty interval is estimated; retain original node-bootstrap coefficient separately.',
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, default=SOURCE)
    p.add_argument('--out', type=Path, default=None)
    a = p.parse_args()
    raw = a.source.read_bytes()
    report = derive(json.loads(raw))
    report['source_file_sha256'] = hashlib.sha256(raw).hexdigest()
    encoded = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    if a.out is None:
        print(encoded, end='')
    else:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(encoded, encoding='utf-8')


if __name__ == '__main__':
    main()
