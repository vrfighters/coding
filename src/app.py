import os
import sys
import random
import datetime
import time
import requests
import json
import traceback
import threading
import logging
from flask import Flask, jsonify, request, current_app, g, render_template
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CUR_PATH)
from conf import config
from utils.mlogging import TimedRotatingFileHandler_MP
from handlers.poi_handler import PoiHandler
from handlers.geo_handler import GeoHandler
from handlers.poi_top_handler import PoiTopHandler
from handlers.poi_cluster_handler import PoiClusterHandler


app = Flask("recsys")

def init_logger():
    app.logger.name = "recsys"
    handler = TimedRotatingFileHandler_MP(config.log_path, when='D', backupCount=7)
    formatter = logging.Formatter("%(asctime)s ◊ %(filename)s[line:%(lineno)d] ◊ %(levelname)s ◊ %(message)s")
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    ctx = app.app_context()
    ctx.push()
    current_app.logger.info("server start")

init_logger()

main_logger = logging.getLogger("recsys")

SERVICE_HANDLER_DICT = {
    "poi": PoiHandler,
    "poi_top": PoiTopHandler,
    "geo_info": GeoHandler,
    "cluster_poi": PoiClusterHandler,
}
def build_handler():
    handler_dict = {}
    current_app.logger.info("Constructing handlers...")
    handler_dict = {}
    for srv_name, handler in SERVICE_HANDLER_DICT.items():
        handler_dict[srv_name] = handler()
    main_logger.info("Construct handlers done.")
    return handler_dict
handler_dict = build_handler()

@app.route("/poi-rec", methods=["GET", "POST"])
def poi_rec():
    kwargs = request.args if request.method == "GET" else request.json
    res = handler_dict["poi"].get(kwargs)
    return res


if __name__ == '__main__':
    app.run(**config.server)
