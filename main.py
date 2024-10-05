from typing import Union
import uvicorn
from fastapi import FastAPI
import os
# import pymysql
# test local db server
# conn = pymysql.connect(host='127.0.0.1', user='root', password='rladlgus0625@', db='study_db', charset='utf8')
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8090)
