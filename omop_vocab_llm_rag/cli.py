"""CLI entry point."""
from __future__ import annotations

import argparse
from pathlib import Path

from . import config, guess, guess_check, rag, retrieve, review, verify


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="omop-map")
    p.add_argument(
        "--domain",
        choices=["labs", "meds"],
        required=True,
        help="Domain to operate on: 'labs' (lab tests) or 'meds' (medications)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("build-rag", help="Embed concepts CSV into a FAISS index")
    pb.add_argument("--concepts", type=Path, default=None)
    pb.add_argument("--out", type=Path, default=None)

    pg = sub.add_parser("guess", help="Stage 1: Claude guesses concept + synonyms")
    pg.add_argument("--events", type=Path, default=None)
    pg.add_argument("--out", type=Path, default=None)

    pgc = sub.add_parser(
        "guess-check",
        help="Stage 1.5: re-run guess for stage-1 rows whose concept is null",
    )
    pgc.add_argument("--in", dest="inp", type=Path, default=None)

    pr = sub.add_parser("retrieve", help="Stage 2: RAG retrieval over guesses")
    pr.add_argument("--in", dest="inp", type=Path, default=None)
    pr.add_argument("--rag", type=Path, default=None)
    pr.add_argument("--out", type=Path, default=None)

    pv = sub.add_parser("review", help="Stage 3: Claude picks the best candidate")
    pv.add_argument("--in", dest="inp", type=Path, default=None)
    pv.add_argument("--out", type=Path, default=None)

    pf = sub.add_parser("verify", help="Stage 4: resolve reviewed concept names to concept_ids")
    pf.add_argument("--in", dest="inp", type=Path, default=None)
    pf.add_argument("--rag", type=Path, default=None)
    pf.add_argument("--out", type=Path, default=None)

    pa = sub.add_parser("run-all", help="Run guess + retrieve + review + verify with default paths")
    pa.add_argument("--events", type=Path, default=None)
    pa.add_argument("--rag", type=Path, default=None)

    pq = sub.add_parser("rag-query", help="Ad-hoc RAG query (debugging)")
    pq.add_argument("text")
    pq.add_argument("--k", type=int, default=5)
    pq.add_argument("--rag", type=Path, default=None)

    args = p.parse_args(argv)
    cfg = config.get_domain_config(args.domain)

    if args.cmd == "build-rag":
        rag.build(args.concepts or cfg.CONCEPTS_CSV, args.out or cfg.RAG_DIR)
    elif args.cmd == "guess":
        guess.run(args.events or cfg.EVENTS_CSV, args.out or cfg.STAGE1_OUT, cfg)
    elif args.cmd == "guess-check":
        guess_check.run(args.inp or cfg.STAGE1_OUT, cfg)
    elif args.cmd == "retrieve":
        retrieve.run(args.inp or cfg.STAGE1_OUT, args.rag or cfg.RAG_DIR, args.out or cfg.STAGE2_OUT)
    elif args.cmd == "review":
        review.run(args.inp or cfg.STAGE2_OUT, args.out or cfg.STAGE3_OUT, cfg)
    elif args.cmd == "verify":
        verify.run(args.inp or cfg.STAGE3_OUT, args.rag or cfg.RAG_DIR, args.out or cfg.STAGE4_OUT, cfg)
    elif args.cmd == "run-all":
        guess.run(args.events or cfg.EVENTS_CSV, cfg.STAGE1_OUT, cfg)
        guess_check.run(cfg.STAGE1_OUT, cfg)
        retrieve.run(cfg.STAGE1_OUT, args.rag or cfg.RAG_DIR, cfg.STAGE2_OUT)
        review.run(cfg.STAGE2_OUT, cfg.STAGE3_OUT, cfg)
        verify.run(cfg.STAGE3_OUT, args.rag or cfg.RAG_DIR, cfg.STAGE4_OUT, cfg)
    elif args.cmd == "rag-query":
        idx = rag.load(args.rag or cfg.RAG_DIR)
        for cand in idx.query([args.text], k=args.k)[0]:
            print(f"{cand['score']:.4f}\t{cand['concept_id']}\t{cand['concept_name']}")
