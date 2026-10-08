#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公开题库练题站点 —— 本地 Web 服务

在 5000 端口启动一个静态文件服务器，用于本地预览本目录（site/）下的
练题页面：index.html / app.mjs / core.mjs / render.mjs ...

只依赖 Python 3 标准库，无需 pip 安装任何东西。

用法:
    python server.py                     # 监听 0.0.0.0:5000，根目录 = 脚本所在目录
    python server.py 8000                # 换端口
    python server.py 5000 127.0.0.1      # 只允许本机访问
    python server.py 5000 0.0.0.0 .      # 显式指定站点根目录

浏览器打开:  http://127.0.0.1:5000/
"""

import argparse
import os
import sys
import mimetypes
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# 站点根目录：默认 = 本脚本所在目录（即 site/）
DEFAULT_ROOT = os.path.dirname(os.path.abspath(__file__))

# .mjs / .js 必须以 JavaScript 的 MIME 类型返回，否则浏览器拒绝执行 ES 模块
mimetypes.add_type("text/javascript", ".mjs")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("application/json", ".json")
mimetypes.add_type("application/json", ".jsonl")
mimetypes.add_type("text/markdown", ".md")
mimetypes.add_type("image/svg+xml", ".svg")
mimetypes.add_type("font/woff2", ".woff2")


class SiteHandler(SimpleHTTPRequestHandler):
    """静态文件处理器：本地开发关闭缓存并放开跨域。"""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        # 保留访问日志，输出到 stderr
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))


def main():
    parser = argparse.ArgumentParser(description="公开题库练题站点本地服务")
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=int(os.environ.get("PORT", "5000")),
        help="监听端口，默认 5000",
    )
    parser.add_argument(
        "host",
        nargs="?",
        default="0.0.0.0",
        help="绑定地址，默认 0.0.0.0（局域网可访问；仅本机请填 127.0.0.1）",
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=DEFAULT_ROOT,
        help="站点根目录，默认脚本所在目录",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        parser.error("站点根目录不存在: %s" % root)

    # 用 partial 固定 directory，使服务不依赖启动时的当前工作目录
    handler = partial(SiteHandler, directory=root)
    try:
        httpd = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as e:
        sys.stderr.write("无法在 %s:%d 启动服务: %s\n" % (args.host, args.port, e))
        return 1

    show_host = "127.0.0.1" if args.host in ("0.0.0.0", "", "::") else args.host
    print("公开题库练题站点已启动:")
    print("  访问地址  : http://%s:%d/" % (show_host, args.port))
    print("  站点根目录: %s" % root)
    print("  按 Ctrl+C 停止服务")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n正在停止服务…")
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
