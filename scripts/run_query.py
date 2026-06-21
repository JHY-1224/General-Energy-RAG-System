import argparse
import json

from app.api.dependencies import engine
from app.core.models import QueryRequest


parser = argparse.ArgumentParser()
parser.add_argument("question")
args = parser.parse_args()
print(json.dumps(engine.query(QueryRequest(question=args.question)).model_dump(), ensure_ascii=False, indent=2))
