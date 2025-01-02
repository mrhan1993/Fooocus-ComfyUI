from works.main import app
import json


@app.task
def add(x, y) -> int:
    return x + y


@app.task()
def mul(x, y) -> str:
    return json.dumps({"result": x * y, "status": "Success", "msg": "The task is successfully executed."})
