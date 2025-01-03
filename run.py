import uvicorn
import argparse

from apis.main import app

parse = argparse.ArgumentParser()
parse.add_argument('--host', type=str, default='0.0.0.0')
parse.add_argument('--port', type=int, default=8000)
args = parse.parse_args()

uvicorn.run(app, host=args.host, port=args.port)
