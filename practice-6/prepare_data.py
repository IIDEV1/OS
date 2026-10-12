"""Восстановить учебную выборку из исходного TSV (не нужно для Run All).

Пример: python prepare_data.py women-clothing-accessories.3-class.balanced.csv
"""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from preprocessing import stem_text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    provenance = json.loads((root / 'data/provenance.json').read_text(encoding='utf-8'))
    actual_hash = hashlib.sha256(args.source.read_bytes()).hexdigest()
    if actual_hash != provenance['source_sha256']:
        raise ValueError('SHA-256 исходного файла отличается от использованной версии.')
    raw = pd.read_csv(args.source, sep='\t')
    raw['source_row'] = raw.index + 2
    raw = raw.dropna(subset=['review', 'sentiment'])
    raw['normalized'] = raw.review.map(stem_text)
    raw = raw[raw.normalized.str.len() > 0]
    counts = raw.groupby('normalized').sentiment.nunique()
    raw = raw[raw.normalized.isin(counts[counts == 1].index)].drop_duplicates('normalized')
    sample = pd.concat([g.sample(n=1000, random_state=42) for _, g in raw.groupby('sentiment')])
    sample = sample.sample(frac=1, random_state=42).reset_index(drop=True)
    sample['sentiment'] = sample.sentiment.replace({'neautral': 'neutral'})
    dest = root / 'data/reviews.csv'
    # Проверяем результат до записи, не заменяя данные при несовпадении.
    csv = sample[['source_row', 'review', 'sentiment']].to_csv(index=False, lineterminator='\r\n')
    encoded = csv.encode('utf-8')
    if hashlib.sha256(encoded).hexdigest() != provenance['sample_sha256']:
        csv = sample[['source_row', 'review', 'sentiment']].to_csv(index=False, lineterminator='\n')
        encoded = csv.encode('utf-8')
        if hashlib.sha256(encoded).hexdigest() != provenance['sample_sha256']:
            raise ValueError('Выборка отличается: проверьте версии pandas и nltk.')
    dest.write_bytes(encoded)
    print('Восстановлено отзывов:', len(sample))


if __name__ == '__main__':
    main()
