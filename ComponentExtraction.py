"""
Author: MarsVegetables
Date: 2025-01-22 21:29:48
LastEditors: MarsVegetables
LastEditTime: 2025-01-22 21:29:48
FilePath: ComponentExtraction.py
"""

class ComponentExtraction:
    def __init__(self, faces, edges, motorcycle_edges):
        self.faces = faces
        self.edges = edges
        self.adj_ve = {}  # key vid, value eid
        self.create_adj_ve()
        self.adj_ff = {i: set() for i in range(len(faces))} # key : face idx, value : face idx
        self.adj_ef = {i: set() for i in range(len(self.edges))} # key : edge idx, value : face idx
        self.adj_fe = {i: set() for i in range(len(faces))} # key : face idx, value : edge idx
        self.motorcycle_edges = motorcycle_edges
        self.me_idx_set = set() # a set contains edge id of motorcycle_edges
        self.create_motorcycle_edges_idx_set()
        self.create_adj_dict()
        self.face_components = self.extract_face_components()

    def create_adj_ve(self):
        for eid, edge in enumerate(self.edges):
            for vid in edge:
                if vid not in self.adj_ve:
                    self.adj_ve[vid] = set()
                self.adj_ve[vid].add(eid)

    def create_motorcycle_edges_idx_set(self):
        for m_edge in self.motorcycle_edges:
            for vid in m_edge:
                for eid in self.adj_ve[vid]:
                    if set(sorted(m_edge)) == set(self.edges[eid]):
                        self.me_idx_set.add(eid)
        return

    def create_adj_dict(self):
        for fid, face in enumerate(self.faces):
            face_eids = set()
            for vid in face:
                tmp_eids = self.adj_ve[vid]
                for eid in tmp_eids:
                    if len(set(self.edges[eid]) & set(face)) == 2:
                        face_eids.add(eid)
                        self.adj_ef[eid].add(fid)

            self.adj_fe[fid].update(face_eids)

        for i in self.adj_ef:
            for f in self.adj_ef[i]:
                self.adj_ff[f].update(self.adj_ef[i])
                self.adj_ff[f].remove(f)

    def extract_face_components(self):
        visited_fids = set()
        components = []
        for i in self.adj_ff:
            if i in visited_fids:
                continue
            face_component = self.tracing_faces(i)
            visited_fids.update(face_component)
            components.append(face_component)
        return components

    def tracing_faces(self, fid):
        component_fids = set()
        bfs = [fid]
        while bfs:
            next_fid = bfs.pop()
            if next_fid in component_fids:
                continue
            component_fids.add(next_fid)
            face_eids = self.adj_fe[next_fid]
            for eid in face_eids:
                bfs.extend(self.get_opposite_face(eid))
        return component_fids


    def get_opposite_face(self, eid):
        if eid in self.me_idx_set:
            return []
        nfids = self.adj_ef[eid]
        return nfids