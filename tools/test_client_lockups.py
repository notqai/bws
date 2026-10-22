import ast, collections, pathlib, unittest

SRC = pathlib.Path(__file__).with_name("generate_site.py")

def clients():
    for node in ast.parse(SRC.read_text()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "CLIENTS" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("CLIENTS not found")

class ClientLockups(unittest.TestCase):
    def test_shared_logos_have_distinct_lockups(self):
        by_logo = collections.defaultdict(list)
        for row in clients():
            self.assertEqual(len(row), 6, row)
            if row[1]: by_logo[row[1]].append(row)
        for logo, rows in by_logo.items():
            if len(rows) > 1:
                names = [r[5] for r in rows]
                self.assertTrue(all(names), f"{logo}: every card sharing a logo needs a lockup name")
                self.assertEqual(len(set(names)), len(names), f"{logo}: duplicate lockup names {names}")

if __name__ == "__main__":
    unittest.main()
