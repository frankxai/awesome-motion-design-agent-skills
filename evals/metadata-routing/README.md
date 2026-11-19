# Discovery metadata and retrieval

Measured on 19 November 2026. A fixed local encoder ranked the same five first-party skills for each of PR #41's 60 prompts. The control indexed the folder name with hyphens replaced by spaces. The treatment appended the exact shipped description. Both arms used the identical model, tokenizer, prompts, mean pooling, normalized embeddings and cosine ranking. All inference ran on CPU.

| Correct first choice on positive prompts | Name | Name and description |
| --- | ---: | ---: |
| Generative media director | 1/6 | 4/6 |
| Motion director | 3/6 | 3/6 |
| Remotion video agent | 6/6 | 6/6 |
| Site motion excellence director | 5/6 | 4/6 |
| Web motion auditor | 2/6 | 5/6 |
| All five | 17/30 | 22/30 |

On the 30 negative prompts, the router selected the explicitly prohibited skill eight times from names and seven times from names plus descriptions. The experiment forced a winner among five candidates, including for prompts unrelated to motion. It cannot establish an abstention rate, native agent activation, or production conversion. These maintainer-written prompts are a development set. The site director lost one positive under the treatment, even as the aggregate improved. Validate changes against independently authored prompts before adopting a new description.

## Reproduce

Use Python 3.12, `numpy==2.3.5`, `onnxruntime==1.23.2`, `tokenizers==0.22.2` and PyYAML. Obtain [the ONNX file](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/main/onnx/model_quint8_avx2.onnx) and [tokenizer](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/main/tokenizer.json) from the upstream Apache-2.0 model. Place the two files together in a local directory. The script verifies both SHA-256 digests before inference. No model downloads or API calls run in the test.

```sh
git fetch origin refs/pull/41/head
git worktree add --detach /tmp/motion-routing-fixtures 1cb5265957ff724cde8bda38c649261d778c9fba
git worktree add --detach /tmp/motion-routing-source e7dc6e2e728c918ffcea5edb2d7c94e2a6f7785d
python evals/metadata-routing/check.py --model /path/to/model-files --skills-repo /tmp/motion-routing-source --fixture-repo /tmp/motion-routing-fixtures --output /tmp/routing.json
```

[Per-prompt predictions](results.json) identify the reviewed fixture by revision, skill name, case label and zero-based case index. The scorer compares predictions to fixed labels without a subjective rating. A deterministic repeat generated identical counts. This optional test has no CI trigger.
