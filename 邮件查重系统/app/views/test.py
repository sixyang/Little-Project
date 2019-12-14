from random import randrange

from flask import Flask, render_template, Blueprint

from pyecharts import options as opts
from pyecharts.charts import Bar


pp = Blueprint('hello', __name__)

def bar_base() -> Bar:
    c = (
        Bar()
        .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
        .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
        .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
        .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
    )
    return c

@pp.route("/barChart", methods=["GET"])
def get_bar_chart():
    c = bar_base()
    return c.dump_options_with_quotes()