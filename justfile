set dotenv-load := true

pipeline := "uv run --project research/pipeline"

harvest slug:
    {{pipeline}} python -m companmem_pipeline.harvest --slug {{slug}}

harvest-inventory slug:
    {{pipeline}} python -m companmem_pipeline.harvest --slug {{slug}} --inventory

harvest-all:
    {{pipeline}} python -m companmem_pipeline.harvest --all

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

audit-write-all:
    {{pipeline}} python -m companmem_pipeline.extract --all
    {{pipeline}} python -m companmem_pipeline.fold --all
    {{pipeline}} python -m companmem_pipeline.apply --all --write

lint-audits:
    {{pipeline}} python -m companmem_pipeline.lint

synthesize:
    {{pipeline}} python -m companmem_pipeline.synthesize

test-pipeline:
    {{pipeline}} pytest research/pipeline/tests
