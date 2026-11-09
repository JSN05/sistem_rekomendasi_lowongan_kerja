"""Knowledge Graph NetworkX (Bab 2.5 paper): user node, job node, attribute node."""
import threading
import uuid
from typing import Optional

import networkx as nx

import matching as m

ATTRIBUTES = ["position", "location", "education", "experience", "job_type", "salary", "gender"]
RELATIONS = {"position": "posisi", "location": "lokasi", "education": "pendidikan",
             "experience": "pengalaman", "job_type": "tipe pekerjaan", "salary": "gaji",
             "gender": "gender"}


class JobKnowledgeGraph:
    def __init__(self, records: list[dict], salary_basis: str = "min"):
        self.G = nx.Graph()
        self.salary_basis = salary_basis
        self.job_nodes: list[str] = []
        self._lock = threading.RLock()   # user node ditambah/dihapus sementara pada graph bersama
        for rec in records:
            self._add_job(rec)

    # ------------------------------------------------------------ build graph
    def _attribute_node(self, attr: str, value) -> str:
        node_id = f"{RELATIONS[attr]}:{value}"
        if node_id not in self.G:
            self.G.add_node(node_id, kind="attribute", attribute=attr, value=value)
        return node_id

    def _job_attribute_values(self, rec: dict) -> dict:
        city, prov = rec.get("location_city"), rec.get("location_province")
        values = {
            "position": rec.get("job_title"),
            "location": ", ".join(x for x in (city, prov) if x) or None,
            "education": rec.get("education_level"),
            "experience": rec.get("experience") if rec.get("experience") is not None else 0,
            "job_type": rec.get("job_type"),
            "salary": m.salary_reference(rec, self.salary_basis),
            "gender": m.canonical_gender(rec.get("gender"), job=True),
        }
        return {k: v for k, v in values.items() if v not in (None, "")}

    def _add_job(self, rec: dict) -> None:
        node = f"job:{rec['job_id']}"
        self.G.add_node(
            node, kind="job", job_id=rec["job_id"],
            closed=bool(rec.get("is_closed")),
            highlighted=bool(rec.get("is_highlighted")),
            salary_missing=bool(rec.get("salary_is_missing")),
        )
        self.job_nodes.append(node)
        for attr, value in self._job_attribute_values(rec).items():
            self.G.add_edge(node, self._attribute_node(attr, value), relation=RELATIONS[attr])

    # ------------------------------------------------------------- user node
    @staticmethod
    def _user_values(c: dict) -> dict:
        v = {}
        if c.get("position"): v["position"] = m.norm(c["position"])
        if c.get("location"): v["location"] = m.norm(c["location"])
        if c.get("education"): v["education"] = m.norm(c["education"])
        if c.get("experience") is not None: v["experience"] = int(c["experience"])
        if c.get("jobType"): v["job_type"] = m.canonical_job_type(c["jobType"])
        if c.get("salaryMin") is not None: v["salary"] = int(c["salaryMin"])
        if c.get("gender"): v["gender"] = m.canonical_gender(c["gender"])
        return v

    def _values(self, node: str) -> dict:
        out = {}
        for nbr in self.G[node]:
            data = self.G.nodes[nbr]
            if data.get("kind") == "attribute":
                out[data["attribute"]] = data["value"]
        return out

    # ---------------------------------------------------------- matching
    @staticmethod
    def _match_flags(u: dict, j: dict) -> dict:
        return {
            "position": m.match_position(u.get("position"), j.get("position")),
            "location": m.match_location(u.get("location"), j.get("location")),
            "education": m.match_education(u.get("education"), j.get("education")),
            "experience": m.match_experience(u.get("experience"), j.get("experience")),
            "job_type": m.match_job_type(u.get("job_type"), j.get("job_type")),
            "salary": m.match_salary(u.get("salary"), j.get("salary")),
            "gender": m.match_gender(u.get("gender"), j.get("gender")),
        }

    def recommend(self, criteria: dict, include_closed: bool = False) -> list[dict]:
        """Tambahkan user node, hitung skor tiap lowongan, urutkan, lalu hapus user node."""
        user_vals = self._user_values(criteria)
        user_node = f"user:{uuid.uuid4().hex}"
        results = []
        with self._lock:
            created = []
            self.G.add_node(user_node, kind="user")
            for attr, value in user_vals.items():
                attr_id = f"{RELATIONS[attr]}:{value}"
                if attr_id not in self.G:
                    created.append(attr_id)
                self.G.add_edge(user_node, self._attribute_node(attr, value), relation=RELATIONS[attr])
            try:
                u = self._values(user_node)
                for job in self.job_nodes:
                    meta = self.G.nodes[job]
                    if meta["closed"] and not include_closed:
                        continue
                    flags = self._match_flags(u, self._values(job))
                    score = sum(flags.values())
                    results.append({
                        "job_id": meta["job_id"],
                        "score": score,
                        "percentage": round(score / len(ATTRIBUTES) * 100, 2),
                        "flags": {k: int(v) for k, v in flags.items()},
                        "_sort": (-score, not meta["highlighted"], meta["salary_missing"], meta["job_id"]),
                    })
            finally:
                self.G.remove_node(user_node)
                for attr_id in created:
                    if attr_id in self.G and self.G.degree(attr_id) == 0:
                        self.G.remove_node(attr_id)
        results.sort(key=lambda r: r["_sort"])
        for r in results:
            del r["_sort"]
        return results

    def stats(self) -> dict:
        kinds = {}
        for _, d in self.G.nodes(data=True):
            kinds[d.get("kind")] = kinds.get(d.get("kind"), 0) + 1
        return {"nodes": self.G.number_of_nodes(), "edges": self.G.number_of_edges(), **kinds}
