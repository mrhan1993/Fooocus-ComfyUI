"""
SQLite client
"""
import logging
import os
import time
import platform
from datetime import datetime
from typing import Optional
import copy

from sqlalchemy import Integer, Float, VARCHAR, Boolean, JSON, Text, create_engine, text
from sqlalchemy.orm import declarative_base, Session, Mapped, mapped_column


Base = declarative_base()



engine = create_engine(connection_uri)

session = Session(engine)
Base.metadata.create_all(engine, checkfirst=True)
session.close()


def convert_to_dict_list(obj_list: list[object]) -> list[dict]:
    """
    Convert a list of objects to a list of dictionaries.
    Args:
        obj_list:

    Returns:
        dict_list:
    """
    dict_list = []
    for obj in obj_list:
        # 将对象属性转化为字典键值对
        dict_obj = {}
        for attr, value in vars(obj).items():
            if (
                not callable(value)
                and not attr.startswith("__")
                and not attr.startswith("_")
            ):
                dict_obj[attr] = value
        task_info = {
            "task_id": obj.task_id,
            "task_type": obj.task_type,
            "task_in_queue_mills": obj.task_in_queue_mills,
            "task_start_mills": obj.task_start_mills,
            "task_finish_mills": obj.task_finish_mills,
            "result_url": obj.result_url,
            "finish_reason": obj.finish_reason,
            "date_time": datetime.fromtimestamp(obj.date_time).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }
        del dict_obj["task_id"]
        del dict_obj["task_type"]
        del dict_obj['task_in_queue_mills']
        del dict_obj['task_start_mills']
        del dict_obj['task_finish_mills']
        del dict_obj["result_url"]
        del dict_obj["finish_reason"]
        del dict_obj["date_time"]
        dict_list.append({"params": dict_obj, "task_info": task_info})
    return dict_list


class MySQLAlchemy:
    """
    MySQLAlchemy, a toolkit for managing SQLAlchemy connections and sessions.

    :param uri: SQLAlchemy connection URI
    """

    def __init__(self, uri: str):
        # 'mysql+pymysql://{username}:{password}@{host}:{port}/{database}'
        self.engine = create_engine(uri)
        self.session = Session(self.engine)
        self.add_columns_if_not_exists()

    def add_columns_if_not_exists(self):
        """
        Add new columns but keep old data. This function runs automatically.
        """
        table_name = GenerateRecord.__tablename__
        # Check if the table exists
        result = self.session.execute(
            text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"))
        if not result.fetchone():
            return

        result = self.session.execute(text(f"PRAGMA table_info({table_name});"))
        columns = [row[1] for row in result.fetchall()]
        try:
            if 'task_in_queue_mills' not in columns:
                self.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN task_in_queue_mills INTEGER DEFAULT 0;"))
            if 'task_start_mills' not in columns:
                self.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN task_start_mills INTEGER DEFAULT 0;"))
            if 'task_finish_mills' not in columns:
                self.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN task_finish_mills INTEGER DEFAULT 0;"))
        except Exception as e:
            logging.error(f"add new columns failed {e}")

    def store_history(self, record: dict) -> None:
        """
        Store history to database
        :param record:
        :return:
        """
        serialized_image_prompts = [
            (cn_stop, cn_wight, cn_type)
            for arr, cn_stop, cn_wight, cn_type in record['image_prompts']
        ]
        record['image_prompts'] = serialized_image_prompts
        self.session.add_all([GenerateRecord(**record)])
        self.session.commit()

    def get_history(
        self,
        task_id: str | None = None,
        page: int = 0,
        page_size: int = 20,
        order_by: str = "date_time",
    ) -> list:
        """
        Get history from database
        :param task_id:
        :param page:
        :param page_size:
        :param order_by:
        :return:
        """
        if task_id is not None:
            res = (
                self.session.query(GenerateRecord)
                .filter(GenerateRecord.task_id == task_id)
                .all()
            )
            if len(res) == 0:
                return []
            return convert_to_dict_list(res)

        res = (
            self.session.query(GenerateRecord)
            .order_by(getattr(GenerateRecord, order_by).desc())
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )
        if len(res) == 0:
            return []
        return convert_to_dict_list(res)

    def delete(self, task_id: str) -> None:
        """
        Delete item from database
        :param task_id:
        :return:
        """
        self.session.query(GenerateRecord).filter(GenerateRecord.task_id == task_id).delete()
        self.session.commit()


db = MySQLAlchemy(uri=connection_uri)


def req_to_dict(req: dict) -> dict:
    """
    Convert request to dictionary
    Args:
        req:

    Returns:

    """
    req["loras"] = [{"model_name": lora[0], "weight": lora[1]} for lora in req["loras"]]
    # req["advanced_params"] = dict(zip(adv_params_keys, req["advanced_params"]))
    req["image_prompts"] = [
        {"cn_img": "", "cn_stop": image[1], "cn_weight": image[2], "cn_type": image[3]}
        for image in req["image_prompts"]
    ]
    del req["inpaint_input_image"]
    del req["uov_input_image"]
    return req


def add_history(
    params: dict, task_info: dict, result_url: str, finish_reason: str
) -> None:
    """
    Store history to database
    Args:
        params:
        task_info:
        result_url:
        finish_reason:

    Returns:

    """
    adv = copy.deepcopy(params["advanced_params"])
    params["advanced_params"] = adv.__dict__
    params["date_time"] = int(time.time())
    for k, v in task_info.items():
        params[k] = v
    params["result_url"] = result_url
    params["finish_reason"] = finish_reason

    del params["enhance_input_image"]
    del params["enhance_checkbox"]
    del params["enhance_uov_method"]
    del params["enhance_uov_processing_order"]
    del params["enhance_uov_prompt_type"]
    del params["save_final_enhanced_image_only"]
    del params["enhance_ctrlnets"]
    del params["inpaint_input_image"]
    del params["uov_input_image"]
    del params["save_extension"]
    del params["save_meta"]
    del params["save_name"]
    del params["meta_scheme"]
    del params["read_wildcards_in_order"]
    del params["current_tab"]

    db.store_history(params)


def query_history(
        task_id: str = None,
        page: int = 0,
        page_size: int = 20,
        order_by: str = "date_time"
) -> list:
    """
    Query history from database
    Args:
        task_id:
        page:
        page_size:
        order_by:

    Returns:

    """
    return db.get_history(
        task_id=task_id, page=page, page_size=page_size, order_by=order_by
    )


def delete_item(item_id: str) -> None:
    """
    Delete item from database
    Args:
        item_id:
    Returns:
    """
    db.delete(item_id)
