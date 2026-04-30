"""CLI entry point."""
from __future__ import annotations

import argparse
from pathlib import Path

from . import config, guess, guess_check, rag, retrieve, review, verify


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="omop-map")
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("build-rag", help="Embed lab_concepts.csv into a FAISS index")
    pb.add_argument("--concepts", type=Path, default=config.CONCEPTS_CSV)
    pb.add_argument("--out", type=Path, default=config.RAG_DIR)

    pg = sub.add_parser("guess", help="Stage 1: Claude guesses concept + synonyms")
    pg.add_argument("--events", type=Path, default=config.EVENTS_CSV)
    pg.add_argument("--out", type=Path, default=config.STAGE1_OUT)

    pgc = sub.add_parser(
        "guess-check",
        help="Stage 1.5: re-run guess for stage-1 rows whose concept is null",
    )
    pgc.add_argument("--in", dest="inp", type=Path, default=config.STAGE1_OUT)

    pr = sub.add_parser("retrieve", help="Stage 2: RAG retrieval over guesses")
    pr.add_argument("--in", dest="inp", type=Path, default=config.STAGE1_OUT)
    pr.add_argument("--rag", type=Path, default=config.RAG_DIR)
    pr.add_argument("--out", type=Path, default=config.STAGE2_OUT)

    pv = sub.add_parser("review", help="Stage 3: Claude picks the best candidate")
    pv.add_argument("--in", dest="inp", type=Path, default=config.STAGE2_OUT)
    pv.add_argument("--out", type=Path, default=config.STAGE3_OUT)

    pf = sub.add_parser("verify", help="Stage 4: resolve reviewed concept names to concept_ids")
    pf.add_argument("--in", dest="inp", type=Path, default=config.STAGE3_OUT)
    pf.add_argument("--rag", type=Path, default=config.RAG_DIR)
    pf.add_argument("--out", type=Path, default=config.STAGE4_OUT)

    pa = sub.add_parser("run-all", help="Run guess + retrieve + review + verify with default paths")
    pa.add_argument("--events", type=Path, default=config.EVENTS_CSV)
    pa.add_argument("--rag", type=Path, default=config.RAG_DIR)

    pq = sub.add_parser("rag-query", help="Ad-hoc RAG query (debugging)")
    pq.add_argument("text")
    pq.add_argument("--k", type=int, default=5)
    pq.add_argument("--rag", type=Path, default=config.RAG_DIR)

    args = p.parse_args(argv)

    if args.cmd == "build-rag":
        rag.build(args.concepts, args.out)
    elif args.cmd == "guess":
        guess.run(args.events, args.out)
    elif args.cmd == "guess-check":
        guess_check.run(args.inp)
    elif args.cmd == "retrieve":
        retrieve.run(args.inp, args.rag, args.out)
    elif args.cmd == "review":
        review.run(args.inp, args.out)
    elif args.cmd == "verify":
        verify.run(args.inp, args.rag, args.out)
    elif args.cmd == "run-all":
        guess.run(args.events, config.STAGE1_OUT)
        guess_check.run(config.STAGE1_OUT)
        retrieve.run(config.STAGE1_OUT, args.rag, config.STAGE2_OUT)
        review.run(config.STAGE2_OUT, config.STAGE3_OUT)
        verify.run(config.STAGE3_OUT, args.rag, config.STAGE4_OUT)
    elif args.cmd == "rag-query":
        idx = rag.load(args.rag)
        for cand in idx.query([args.text], k=args.k)[0]:
            print(f"{cand['score']:.4f}\t{cand['concept_id']}\t{cand['concept_name']}")
