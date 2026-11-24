"""Graph edges and chains: literal, chronological, honestly graded."""
import unittest

from tests.support import branches
from shared.formula import NULL
from shared.graph import Chronology, GRADES
from shared.languages import BRANCHES


class Graph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = branches()

    def test_edges_come_from_literal_pairs(self):
        for b in BRANCHES:
            pairs = {p['id']: p for p in self.data[b]['pairs']}
            for e in self.data[b]['edges']:
                self.assertNotEqual(e['a'], e['b'])
                self.assertNotEqual(e['a'], NULL)
                for pid in e['pairs']:
                    p = pairs[pid]
                    self.assertIn(p['kind'], ('literal', 'loss'))
                    self.assertEqual((p['a'], p['b'], p['position'], p['era']), (e['a'], e['b'], e['position'], e['era']))

    def test_every_literal_pair_is_an_edge(self):
        for b in BRANCHES:
            in_edges = {pid for e in self.data[b]['edges'] for pid in e['pairs']}
            for p in self.data[b]['pairs']:
                self.assertEqual(p['kind'] in ('literal', 'loss'), p['id'] in in_edges, p['id'])

    def test_conditions_are_kept(self):
        # AQ. voiced stops became spirants *except after nasals*: b > β keeps its exceptions
        edges = [e for e in self.data['quenya']['edges'] if e['marker'] == 'AQ.' and e['a'] == 'b' and e['b'] == 'β']
        self.assertTrue(edges)
        self.assertTrue(all(e['conditional'] and 'mb > mb' in e['exceptions'] for e in edges))

    def test_chains_follow_chronology(self):
        for b in BRANCHES:
            model = {'rules': self.data[b]['rules']}
            chrono = Chronology(model)
            edges = {e['id']: e for e in self.data[b]['edges']}
            for c in self.data[b]['chains']:
                path = [edges[i] for i in c['steps']]
                self.assertEqual(len(c['states']), len(path) + 1)
                self.assertEqual(c['states'], [path[0]['a']] + [e['b'] for e in path])
                for e1, e2, t in zip(path, path[1:], c['transitions']):
                    self.assertEqual(chrono.transition(e1, e2), t)
                    self.assertNotEqual(t, 'contradicted')
                    self.assertEqual(e1['era'], e2['era'])

    def test_grades(self):
        for b in BRANCHES:
            edges = {e['id']: e for e in self.data[b]['edges']}
            derivs = {d['id']: d for d in self.data[b]['derivations']}
            for c in self.data[b]['chains']:
                self.assertIn(c['grade'], GRADES)
                path = [edges[i] for i in c['steps']]
                if c['grade'] == 'A':
                    self.assertTrue(c['attested_in'])
                    d = derivs[c['attested_in'][0]]
                    self.assertFalse(d['deleted'])
                    pos = -1
                    for e in path:  # the steps occur in this order in the derivation
                        later = [i for i, s in enumerate(d['steps']) if s['pair'] in e['pairs'] and i > pos]
                        self.assertTrue(later, c['id'])
                        pos = later[0]
                else:
                    self.assertEqual(c['attested_count'], 0)
                if c['grade'] in ('B', 'C'):
                    self.assertTrue(all(e['examples'] > 0 for e in path))
                if c['grade'] == 'B':
                    self.assertTrue(all(t in ('stage', 'ordered') for t in c['transitions']))
                if c['grade'] == 'D':
                    self.assertTrue(any(e['examples'] == 0 for e in path))

    def test_chain_ids_unique(self):
        for b in BRANCHES:
            ids = [c['id'] for c in self.data[b]['chains']]
            self.assertEqual(len(ids), len(set(ids)))


if __name__ == '__main__':
    unittest.main()
