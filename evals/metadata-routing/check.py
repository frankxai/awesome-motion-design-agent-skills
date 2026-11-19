"""Paired top-one retrieval on a maintained prompt bank with a local, pinned encoder."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
import tokenizers
import yaml

EXPECTED = {
    'model_quint8_avx2.onnx': 'b941bf19f1f1283680f449fa6a7336bb5600bdcd5f84d10ddc5cd72218a0fd21',
    'tokenizer.json': 'be50c3628f2bf5bb5e3a7f17b1f74611b2561a3a27eeab05e5aa30f411572037',
}


def revision(path):
    return subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('model', 'skills-repo', 'fixture-repo', 'output'):
        parser.add_argument('--' + option, required=True, type=Path)
    args = parser.parse_args()
    for repo, relative in [(args.skills_repo, 'skills'), (args.fixture_repo, 'evals/triggers')]:
        changed = subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain',
                                           '--', relative], text=True)
        if changed:
            raise ValueError(f'Use a clean checkout for {relative} so the recorded revision is accurate')
    for filename, digest in EXPECTED.items():
        if hashlib.sha256((args.model / filename).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Unexpected digest for {filename}')
    tokenizer = Tokenizer.from_file(str(args.model / 'tokenizer.json'))
    tokenizer.enable_truncation(max_length=256)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    encoder = ort.InferenceSession(str(args.model / 'model_quint8_avx2.onnx'), options,
                                   providers=['CPUExecutionProvider'])

    def vector(text):
        item = tokenizer.encode(text)
        feed = {name: np.array([value], dtype=np.int64)
                for name, value in [('input_ids', item.ids), ('attention_mask', item.attention_mask),
                                    ('token_type_ids', item.type_ids)]}
        state = encoder.run(None, feed)[0][0]
        pooled = state[np.array(item.attention_mask, dtype=bool)].mean(axis=0)
        return pooled / np.linalg.norm(pooled)

    cards = {}
    for file in sorted((args.skills_repo / 'skills').glob('*/SKILL.md')):
        frontmatter = yaml.safe_load(file.read_text().split('---', 2)[1])
        name = frontmatter['name']
        title = name.replace('-', ' ')
        cards[name] = {'name': vector(title), 'description': vector(title + '. ' + frontmatter['description'])}
    cases = []
    for file in sorted((args.fixture_repo / 'evals/triggers').glob('*.json')):
        item = json.loads(file.read_text())
        name = item['skill']
        if name not in cards:
            raise ValueError(f'Missing skill {name}')
        for label in ['should_trigger', 'should_not_trigger']:
            for index, prompt in enumerate(item[label]):
                query = vector(prompt)
                winners = {arm: max(cards, key=lambda skill: float(query @ cards[skill][arm]))
                           for arm in ['name', 'description']}
                cases.append(dict(expectedSkill=name, label=label, index=index, predicted=winners))
    summary = {}
    for label in ['should_trigger', 'should_not_trigger']:
        group = [c for c in cases if c['label'] == label]
        counts = Counter()
        for row in group:
            for arm, selected in row['predicted'].items():
                if selected == row['expectedSkill']:
                    counts[arm] += 1
        summary[label] = {'prompts': len(group), 'nameTop1IsLabeledSkill': counts['name'],
                          'descriptionTop1IsLabeledSkill': counts['description']}
    data = dict(model='sentence-transformers/all-MiniLM-L6-v2, ONNX quint8 AVX2',
                modelFiles=EXPECTED, onnxruntime=ort.__version__, tokenizers=tokenizers.__version__,
                skillsRevision=revision(args.skills_repo), fixtureRevision=revision(args.fixture_repo),
                comparison='Same five candidates and prompts, unit-normalized mean pooling, cosine top one. '
                           'Name only vs name plus shipped description. No abstention.',
                summary=summary, cases=cases)
    args.output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
