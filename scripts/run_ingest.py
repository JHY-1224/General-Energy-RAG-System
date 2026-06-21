import argparse
import json

from app.api.dependencies import engine
from app.core.models import IngestRequest


parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
print(json.dumps(engine.ingest(IngestRequest(path=args.path)), ensure_ascii=False, indent=2))
