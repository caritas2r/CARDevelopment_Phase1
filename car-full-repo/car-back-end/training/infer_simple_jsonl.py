#!/usr/bin/env python3
"""
infer_simple_jsonl.py

Token-efficient inference runner:
- Reads template-free segments JSONL
- Runs ONE generate() call per prompt
- Stops when <END_JSON> (or common whitespace-prefixed variants) is emitted
- Extracts + parses first JSON object
- Writes results to output JSONL
"""

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    StoppingCriteria,
    StoppingCriteriaList,
)
from peft import PeftModel


# -----------------------------
# CONFIG
# -----------------------------
BASE_MODEL_ID = "Qwen/Qwen2.5-3B"
ADAPTER_PATH = "outputs/qwen25_3b_base_template_free_json_qlora_v2_ENDJSON_REMOVEDESCAPES"

INPUT_JSONL = "data/test_template_free.jsonl"
OUTPUT_JSONL = "outputs/inference_report_test.jsonl"

END_MARKER = "<END_JSON>"

MAX_NEW_TOKENS = 512
REPETITION_PENALTY = 1.05

TORCH_DTYPE = torch.float16


# -----------------------------
# HELPERS
# -----------------------------
def iter_input_texts_from_segments(example: Dict[str, Any]) -> List[str]:
    out: List[str] = []
    for seg in example.get("segments", []):
        if seg.get("label") is False:
            txt = (seg.get("text") or "").strip()
            if txt:
                out.append(txt)
    return out


@dataclass
class JsonExtractResult:
    json_text: Optional[str]
    error: Optional[str]


def extract_first_json_object(text: str) -> JsonExtractResult:
    start = text.find("{")
    if start == -1:
        return JsonExtractResult(None, "No '{' found")

    in_string = False
    escape = False
    depth = 0

    for i in range(start, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return JsonExtractResult(text[start:i + 1], None)

    return JsonExtractResult(None, "Unclosed JSON object")


# -----------------------------
# STOPPING CRITERIA
# -----------------------------
class StopOnAnyTokenSequence(StoppingCriteria):
    """
    Stops generation if the last tokens match any of the provided stop token sequences.
    This is more robust than matching only tokenizer.encode("<END_JSON>") because
    the model often emits "\n<END_JSON>" or " <END_JSON>".
    """
    def __init__(self, stop_seqs: List[List[int]]):
        super().__init__()
        self.stop_seqs = [s for s in stop_seqs if s]  # drop empties
        self.max_n = max((len(s) for s in self.stop_seqs), default=0)
        self.matched: Optional[List[int]] = None

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if self.max_n == 0:
            return False

        # Check each stop sequence as a suffix
        ids = input_ids[0].tolist()
        for s in self.stop_seqs:
            n = len(s)
            if len(ids) >= n and ids[-n:] == s:
                self.matched = s
                return True
        return False


def build_stop_sequences(tokenizer: AutoTokenizer, marker: str) -> List[List[int]]:
    # Include common whitespace-prefix variants that change tokenization
    variants = [
        marker,
        "\n" + marker,
        " " + marker,
        "\r\n" + marker,
    ]
    seqs: List[List[int]] = []
    for v in variants:
        ids = tokenizer.encode(v, add_special_tokens=False)
        if ids:
            seqs.append(ids)
    return seqs


# -----------------------------
# LOAD MODEL
# -----------------------------
def load_model_and_tokenizer():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True)
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL_ID,
        torch_dtype=TORCH_DTYPE,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
    model.eval()
    return model, tokenizer


# -----------------------------
# MAIN
# -----------------------------
def main():
    model, tokenizer = load_model_and_tokenizer()

    stop_seqs = build_stop_sequences(tokenizer, END_MARKER)
    stopper = StopOnAnyTokenSequence(stop_seqs)
    stopping = StoppingCriteriaList([stopper]) if stop_seqs else None

    print(f"Adapter path: {ADAPTER_PATH}", flush=True)
    print(f"Loaded base model: {BASE_MODEL_ID}", flush=True)
    if not stop_seqs:
        print(f"WARNING: Could not tokenize END_MARKER variants; stopping disabled.", flush=True)
    else:
        print(f"Stop sequences (token lens): {[len(s) for s in stop_seqs]}", flush=True)

    # Load prompts
    prompts: List[Tuple[int, int, str]] = []
    with open(INPUT_JSONL, "r", encoding="utf-8") as f:
        for li, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            ex = json.loads(line)
            for si, p in enumerate(iter_input_texts_from_segments(ex)):
                prompts.append((li, si, p))

    print(f"Loaded {len(prompts)} prompts from {INPUT_JSONL}", flush=True)

    with open(OUTPUT_JSONL, "w", encoding="utf-8") as f_out:
        for idx, (li, si, prompt) in enumerate(prompts, 1):
            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            prompt_len = int(inputs["input_ids"].shape[1])

            # Always supply a valid attention mask
            inputs["attention_mask"] = torch.ones_like(inputs["input_ids"], device=inputs["input_ids"].device)

            if torch.cuda.is_available():
                torch.cuda.synchronize()
            t0 = time.time()

            gen_kwargs = dict(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                repetition_penalty=REPETITION_PENALTY,
                do_sample=False,
                use_cache=True,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            if stopping is not None:
                # reset match state for this run
                stopper.matched = None
                gen_kwargs["stopping_criteria"] = stopping

            with torch.no_grad():
                gen_ids = model.generate(**gen_kwargs)

            if torch.cuda.is_available():
                torch.cuda.synchronize()
            dt = time.time() - t0

            gen_new_tokens = int(gen_ids.shape[1] - prompt_len)

            raw = tokenizer.decode(gen_ids[0, prompt_len:], skip_special_tokens=True)

            # Determine stop reason based on whether stopping criteria matched
            stop_reason = "cap"
            if stopping is not None and stopper.matched is not None:
                stop_reason = "end_marker_token_stop"

            # Regardless, trim at the first visible marker if present
            marker_pos = raw.find(END_MARKER)
            if marker_pos != -1:
                raw = raw[:marker_pos]

            extract = extract_first_json_object(raw)
            parsed = None
            parse_ok = False
            parse_err = None

            if extract.json_text:
                try:
                    parsed = json.loads(extract.json_text)
                    parse_ok = True
                except Exception as e:
                    parse_err = repr(e)
            else:
                parse_err = extract.error

            record = {
                "source_line_index": li,
                "segment_index": si,
                "prompt_len_tokens": prompt_len,
                "generated_len_tokens": gen_new_tokens,
                "runtime_seconds": round(dt, 3),
                "stop_reason": stop_reason,
                "parse_ok": parse_ok,
                "input_text": prompt,
                "raw_generated_text": raw,
                "extracted_json_text": extract.json_text,
                "parse_error": parse_err,
                "parsed_json": parsed if parse_ok else None,
            }

            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(
                f"[{idx}/{len(prompts)}] tokens={gen_new_tokens} time={dt:.2f}s "
                f"stop={stop_reason} parse_ok={parse_ok}",
                flush=True,
            )

    print(f"Done. Wrote {len(prompts)} records to {OUTPUT_JSONL}", flush=True)


if __name__ == "__main__":
    main()
