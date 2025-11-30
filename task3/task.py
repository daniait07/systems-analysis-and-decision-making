import json
from itertools import combinations

def parse_ranking(ranking):
    def expand(item):
        if isinstance(item, list):
            result = []
            for sub in item:
                result.extend(expand(sub))
            return result
        else:
            return [item]
    flat_list = []
    for elem in ranking:
        flat_list.extend(expand(elem))
    return list(dict.fromkeys(flat_list))

def build_matrix(ranking, items):
    size = len(items)
    index = {item: i for i, item in enumerate(items)}
    matrix = [[0]*size for _ in range(size)]
    def fill(r):
        if isinstance(r, list):
            for sub in r:
                fill(sub)
        else:
            pass
    def process(r):
        if isinstance(r, list):
            for i in range(len(r)):
                for j in range(i+1, len(r)):
                    a = r[i]
                    b = r[j]
                    ai, bi = index[a], index[b]
                    matrix[ai][bi] = 1
                    matrix[bi][ai] = 0
    def traverse(r):
        if isinstance(r, list):
            for sub in r:
                traverse(sub)
        else:
            pass
    def fill_matrix_from(r):
        if isinstance(r, list):
            for sub in r:
                fill_matrix_from(sub)
        else:
            pass
    fill(ranking)
    process(ranking)
    return matrix

def transpose(matrix):
    return list(map(list, zip(*matrix)))

def matrix_and(a, b):
    return [[a[i][j] & b[i][j] for j in range(len(a))] for i in range(len(a))]

def matrix_or(a, b):
    return [[a[i][j] | b[i][j] for j in range(len(a))] for i in range(len(a))]

def find_contradictions(YA, YB):
    YB_T = transpose(YB)
    YA_T = transpose(YA)
    P1 = matrix_and(YA, YB_T)
    P2 = matrix_and(YA_T, YB)
    P = matrix_or(P1, P2)
    return P

def find_core(P, items):
    core = []
    size = len(items)
    for i in range(size):
        for j in range(i+1, size):
            if P[i][j] == 0:
                core.append([items[i], items[j]])
    return core

def build_consensus(ranking1, ranking2):
    items = sorted(set(ranking1 + ranking2))
    YA = build_matrix(ranking1, items)
    YB = build_matrix(ranking2, items)
    P = find_contradictions(YA, YB)
    core = find_core(P, items)
    C = matrix_and(YA, YB)
    size = len(items)
    for (i, j) in core:
        idx_i = items.index(i)
        idx_j = items.index(j)
        C[idx_i][idx_j] = 1
        C[idx_j][idx_i] = 1
    return {
        "ядро": core,
        "согласованный порядок": [items[i] for i in range(size) if any(C[i][j] == 1 for j in range(size))]
    }

def main(json_str1, json_str2):
    ranking1 = json.loads(json_str1)
    ranking2 = json.loads(json_str2)
    result = build_consensus(ranking1, ranking2)
    return json.dumps(result)
