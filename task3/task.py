import json
import itertools
from collections import defaultdict, deque

def parse_ranking(ranking):
    result = []
    for group in ranking:
        if isinstance(group, list):
            result.append(list(group))
        else:
            result.append([group])
    return result

def get_objects(r1, r2):
    objs = set()
    for group in r1 + r2:
        if isinstance(group, list):
            objs.update(group)
        else:
            objs.add(group)
    return sorted(objs)

def build_relation_matrix(objects, ranking):
    n = len(objects)
    idx = {obj: i for i, obj in enumerate(objects)}
    matrix = [[0]*n for _ in range(n)]
    for i, group in enumerate(ranking):
        if not isinstance(group, list):
            group = [group]
        for obj1 in group:
            for j, group2 in enumerate(ranking):
                if not isinstance(group2, list):
                    group2 = [group2]
                for obj2 in group2:
                    if i < j or (i == j):
                        matrix[idx[obj1]][idx[obj2]] = 1
    return matrix

def transpose(matrix):
    return [list(row) for row in zip(*matrix)]

def logical_and(m1, m2):
    n = len(m1)
    return [[m1[i][j] & m2[i][j] for j in range(n)] for i in range(n)]

def logical_or(m1, m2):
    n = len(m1)
    return [[m1[i][j] | m2[i][j] for j in range(n)] for i in range(n)]

def get_contradiction_core(YA, YB):
    n = len(YA)
    YAt = transpose(YA)
    YBt = transpose(YB)
    P1 = logical_and(YA, YBt)
    P2 = logical_and(YAt, YB)
    P = logical_or(P1, P2)
    core = []
    for i in range(n):
        for j in range(i+1, n):
            if P[i][j] == 0 and P[j][i] == 0:
                core.append([i, j])
    return core

def modify_C_with_core(C, core):
    for i, j in core:
        C[i][j] = 1
        C[j][i] = 1

def warshall(E):
    n = len(E)
    closure = [row[:] for row in E]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if closure[i][k] and closure[k][j]:
                    closure[i][j] = 1
    return closure

def get_clusters(E_star, objects):
    n = len(E_star)
    visited = [False]*n
    clusters = []
    for i in range(n):
        if not visited[i]:
            cluster = []
            queue = deque([i])
            visited[i] = True
            while queue:
                u = queue.popleft()
                cluster.append(objects[u])
                for v in range(n):
                    if E_star[u][v] and not visited[v]:
                        visited[v] = True
                        queue.append(v)
            clusters.append(sorted(cluster))
    return clusters

def cluster_order(C, clusters, objects):
    idx = {obj: i for i, obj in enumerate(objects)}
    n = len(clusters)
    order = []
    used = [False]*n
    graph = defaultdict(set)
    for i, ci in enumerate(clusters):
        for j, cj in enumerate(clusters):
            if i == j:
                continue
            all_1 = all(C[idx[x]][idx[y]] == 1 for x in ci for y in cj)
            all_0 = all(C[idx[y]][idx[x]] == 0 for x in ci for y in cj)
            if all_1 and all_0:
                graph[i].add(j)
    indegree = [0]*n
    for i in graph:
        for j in graph[i]:
            indegree[j] += 1
    queue = deque([i for i in range(n) if indegree[i] == 0])
    while queue:
        u = queue.popleft()
        order.append(clusters[u])
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)
    for i in range(n):
        if clusters[i] not in order:
            order.append(clusters[i])
    return order

def main(json1, json2):
    r1 = json.loads(json1)
    r2 = json.loads(json2)
    ranking1 = parse_ranking(r1)
    ranking2 = parse_ranking(r2)
    objects = get_objects(ranking1, ranking2)
    YA = build_relation_matrix(objects, ranking1)
    YB = build_relation_matrix(objects, ranking2)
    core_pairs = get_contradiction_core(YA, YB)
    contradiction_core = []
    for i, j in core_pairs:
        contradiction_core.append([objects[i], objects[j]])
    C = logical_and(YA, YB)
    modify_C_with_core(C, core_pairs)
    E = logical_and(C, transpose(C))
    E_star = warshall(E)
    clusters = get_clusters(E_star, objects)
    ordered_clusters = cluster_order(C, clusters, objects)
    result = {
        "ядро": contradiction_core,
        "ранк": [
            cluster if len(cluster) > 1 else cluster[0]
            for cluster in ordered_clusters
        ]
    }
    return json.dumps(result, ensure_ascii=False)

# Пример использования:
if __name__ == "__main__":
    A = '[1,[2,3],4,[5,6,7],8,9,10]'
    B = '[[1,2],[3,4,5],6,7,9,[8,10]]'
    print(main(A, B))
