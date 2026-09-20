set dotenv-load := true

pipeline := "uv run --project research/pipeline"

harvest slug:
    {{pipeline}} python -m companmem_pipeline.harvest --slug {{slug}}

harvest-inventory slug:
    {{pipeline}} python -m companmem_pipeline.harvest --slug {{slug}} --inventory

harvest-all:
    {{pipeline}} python -m companmem_pipeline.harvest --all

harvest-eval slug:
    {{pipeline}} python -m companmem_pipeline.harvest --namespace eval --slug {{slug}}

harvest-eval-inventory slug:
    {{pipeline}} python -m companmem_pipeline.harvest --namespace eval --slug {{slug}} --inventory

extract slug:
    {{pipeline}} python -m companmem_pipeline.extract --slug {{slug}}

fold slug:
    {{pipeline}} python -m companmem_pipeline.fold --slug {{slug}}

audit slug:
    {{pipeline}} python -m companmem_pipeline.extract --slug {{slug}}
    {{pipeline}} python -m companmem_pipeline.fold --slug {{slug}}
    {{pipeline}} python -m companmem_pipeline.apply --slug {{slug}}

audit-write slug:
    {{pipeline}} python -m companmem_pipeline.extract --slug {{slug}}
    {{pipeline}} python -m companmem_pipeline.fold --slug {{slug}}
    {{pipeline}} python -m companmem_pipeline.apply --slug {{slug}} --write

audit-write-eval slug:
    {{pipeline}} python -m companmem_pipeline.extract --namespace eval --slug {{slug}}
    {{pipeline}} python -m companmem_pipeline.fold --namespace eval --slug {{slug}}
    {{pipeline}} python -m companmem_pipeline.apply --namespace eval --slug {{slug}} --write

audit-write-all:
    {{pipeline}} python -m companmem_pipeline.extract --all
    {{pipeline}} python -m companmem_pipeline.fold --all
    {{pipeline}} python -m companmem_pipeline.apply --all --write

lint-audits:
    {{pipeline}} python -m companmem_pipeline.lint

lint-eval-audits:
    {{pipeline}} python -m companmem_pipeline.lint --namespace eval

lint-seed:
    {{pipeline}} python -m companmem_pipeline.seed_lint --check-urls

lint-open-code:
    {{pipeline}} python -m companmem_pipeline.seed_lint --check-open-code --require-clones

synthesize:
    {{pipeline}} python -m companmem_pipeline.synthesize

synthesize-dry-run:
    {{pipeline}} python -m companmem_pipeline.synthesize --dry-run

matrix:
    {{pipeline}} python -m companmem_pipeline.matrix

matrix-dry-run:
    {{pipeline}} python -m companmem_pipeline.matrix --dry-run

test-pipeline:
    {{pipeline}} pytest research/pipeline/tests
