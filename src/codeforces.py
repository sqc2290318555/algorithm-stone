import urllib.request
from bs4 import BeautifulSoup
import urllib.parse
import json
import requests
from sqlitedict import SqliteDict
import util
import os

class PageProblemInfo:
    def __init__(self):
        self.id = ""
        self.url = ""
        self.name = ""
        self.tags = ""
        self.rate = 0
        self.solved = 0

class Codeforces:
    def __init__(self):
        self.dict = self.init_db()

        self.finished = []
        self.flasks = []
        # read user
        p = util.get_root("user", "codeforces")
        entries = os.listdir(p)
        for k in entries:
            if k.endswith(".cpp"):
                self.finished.append(k)
            elif k.endswith(".md"):
                self.flasks.append(k)

    def init_db(self):
        return SqliteDict(util.get_db('codeforces.sqlite'), autocommit=True)

    def check_flask(self, id):
        return next((k for k in self.flasks if k.startswith(f"{id}.")), "")

    def save_problem_meta(self, id, str):
        self.dict[f"codeforces_problem_meta_{id}"] = str
    
    def get_problem_meta(self, id):
        return self.dict.get(f"codeforces_problem_meta_{id}")

    def get_level(self, problem):
        if problem['rating'] > 2000:
            return "Hard"
        return "Medium" if problem['rating'] > 1000 else "Easy"

    def check_finish(self, id):
        return any(k.startswith(f"{id}.") for k in self.finished)

    def get_db_problem(self, id, double):
        v = self.dict.get(f"codeforces_problem_{id}")

        if v is None:
            if double:
                return None

            # 尝试读取小一号的
            new_id = id[:-1]
            new_index = id[-1:]
            if new_index == 'D':
                new_index = 'A'
            elif new_index == 'E':
                new_index = 'B'
            elif new_index == 'F':
                new_index = 'C'
            v = self.get_db_problem("%d%s"%(int(new_id)-1, new_index), True)
            return v
        return json.loads(v)

    def save_db_problem(self, id, data):
        self.dict[f"codeforces_problem_{id}"] = data

    def get_page_problems(self, page_id):
        url = "https://codeforces.com/problemset/page/%d" % (page_id)
        f = urllib.request.urlopen(url)
        content = f.read().decode('utf-8')
        soup = BeautifulSoup(content, 'html.parser')
        p = soup.select("table.problems")[0]
        trs = p.select("tr")
        probleams = []

        for k in trs:
            if len(k.select("td.id")) == 0:
                continue
            info = PageProblemInfo()
            nodeid = k.select("td.id a")[0]
            info.id = nodeid.get_text().strip()

            if self.get_problem_meta(info.id) != None:
                continue

            self.save_problem_meta(info.id, str(k))
            info.url = nodeid["href"].strip()
            info.name = k.select("td")[1].select("div")[0].select("a")[0].get_text().strip()
            info.tags = k.select("td")[1].select("div")[1].select("a")
            probleams.append(info)

        return probleams

    def check_problem(self, id, cid, index):
        if self.get_db_problem(id, False) != None:
            return
        url = f"https://codeforces.com/problemset/problem/{cid}/{index}"

        try:
            f = urllib.request.urlopen(url)
            content = f.read().decode('utf-8')
            self.save_db_problem(id, content)
        except Exception as e:
            print("check problem error:", e)

    def get_update_db_time(self):
        t = self.dict.get("codeforce_update_db_time")
        return 0 if t is None else t

    def save_update_db_time(self):
        self.dict["codeforce_update_db_time"] = util.now()

    def update_db(self):
        t = self.get_update_db_time()
        if util.now()-t < 24*3600*1000:
            return

        url = "https://codeforces.com/api/problemset.problems"

        try:
            f = urllib.request.urlopen(url)
            content = f.read().decode('utf-8')
            qlist = json.loads(content)

            for k in qlist["result"]["problems"]:
                id = str(k['contestId'])+str(k['index'])
                print("id:", id, k['name'])
                value = json.dumps(k)
                self.save_db_problem(id, value)

            self.save_update_db_time()
        except Exception as e:
            print("update_db error:", e)
    
    def close_db(self):
        pass

